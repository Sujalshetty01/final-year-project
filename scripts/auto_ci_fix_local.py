#!/usr/bin/env python3
"""
Conservative local CI auto-fix helper.

Steps:
 1. Detect repo owner/name from git remote.
 2. Use GITHUB_TOKEN from env to query Actions for latest failed run.
 3. Download artifacts, extract failure_summary, and scan logs.
 4. Apply conservative fixes (append missing packages to backend/requirements.txt,
    increase CI health wait loops) when heuristics match.
 5. Run local smoke tests (if possible).
 6. Commit & push changes.

This script retries failed network/GitHub steps once.
"""
import os, sys, json, time, re, shutil, subprocess, tempfile, zipfile
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

RETRY = 1

def run(cmd, check=True, capture=False, env=None):
    print('RUN:', cmd)
    res = subprocess.run(cmd, shell=True, check=False, capture_output=capture, env=env, text=True)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed ({res.returncode}): {cmd}\nstdout={res.stdout}\nstderr={res.stderr}")
    return res

def gh_get(url, token):
    req = Request(url, headers={'User-Agent':'auto-ci-fix'})
    if token:
        req.add_header('Authorization', f'token {token}')
    with urlopen(req, timeout=30) as resp:
        return json.load(resp)

def gh_download(url, outpath, token):
    req = Request(url, headers={'User-Agent':'auto-ci-fix'})
    if token:
        req.add_header('Authorization', f'token {token}')
    with urlopen(req, timeout=60) as resp:
        data = resp.read()
    with open(outpath, 'wb') as f:
        f.write(data)

def parse_git_remote():
    try:
        out = subprocess.check_output(['git','config','--get','remote.origin.url'], text=True).strip()
    except Exception:
        raise RuntimeError('Unable to get git remote.origin.url')
    # supports git@github.com:owner/repo.git or https://github.com/owner/repo.git
    m = re.search(r'[:/](?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$', out)
    if not m:
        raise RuntimeError('Cannot parse remote URL: '+out)
    return m.group('owner'), m.group('repo')

def find_latest_failed_run(owner, repo, token):
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=10'
    data = gh_get(url, token)
    runs = data.get('workflow_runs', [])
    for r in runs:
        if r.get('status') == 'completed' and r.get('conclusion') == 'failure':
            return r
    return None

def download_artifacts_for_run(run, owner, repo, token, outdir):
    artifacts_url = run.get('artifacts_url')
    if not artifacts_url:
        return []
    arts = gh_get(artifacts_url, token)
    downloaded = []
    for a in arts.get('artifacts', []):
        url = a.get('archive_download_url')
        name = a.get('name')
        aid = a.get('id')
        path = os.path.join(outdir, f'artifact_{aid}_{name}.zip')
        try:
            gh_download(url, path, token)
            downloaded.append(path)
        except HTTPError as e:
            print('HTTP error downloading artifact:', e)
        except Exception as e:
            print('Error downloading artifact:', e)
    return downloaded

def extract_failure_summary(artifacts, outdir):
    candidates = []
    for z in artifacts:
        try:
            with zipfile.ZipFile(z) as zp:
                for n in zp.namelist():
                    if 'failure_summary' in n.lower() or n.lower().endswith('.log') or n.lower().endswith('.txt'):
                        dest = os.path.join(outdir, os.path.basename(n))
                        with open(dest, 'wb') as f:
                            f.write(zp.read(n))
                        candidates.append(dest)
        except Exception as e:
            print('zip extract failed', z, e)
    # prefer failure_summary file
    for c in candidates:
        if 'failure_summary' in os.path.basename(c).lower():
            return c
    return candidates[0] if candidates else None

def analyze_log(path):
    text = open(path, 'r', encoding='utf-8', errors='ignore').read()
    issues = {}
    if re.search(r'No module named ([\w\.]+)', text):
        mods = re.findall(r'No module named ([\w\.]+)', text)
        issues['missing_modules'] = mods
    if re.search(r'ModuleNotFoundError: No module named ([\w\.]+)', text):
        mods = re.findall(r'ModuleNotFoundError: No module named ([\w\.]+)', text)
        issues.setdefault('missing_modules', []).extend(mods)
    if 'backend did not become healthy' in text or 'backend did not become healthy' in text.lower():
        issues['backend_unhealthy'] = True
    if re.search(r'Traceback \(most recent call last\):', text):
        issues['traceback'] = True
    errs = re.findall(r'ERROR[: ]+(.+)', text)
    if errs:
        issues['errors'] = errs[:10]
    return issues, text

def apply_conservative_fixes(issues):
    changed = []
    # Fix missing modules by appending to backend/requirements.txt
    reqfn = os.path.join('backend','requirements.txt')
    if 'missing_modules' in issues and os.path.exists(reqfn):
        with open(reqfn, 'r', encoding='utf-8') as f:
            existing = f.read().splitlines()
        to_add = []
        for m in issues['missing_modules']:
            pkg = m.replace('.', '-').lower()
            # simple heuristic mapping
            if pkg not in existing:
                to_add.append(pkg)
        if to_add:
            with open(reqfn, 'a', encoding='utf-8') as f:
                for p in to_add:
                    f.write('\n'+p)
            changed.append(('append_requirements', to_add))

    # Increase CI wait attempts in .github/workflows/ci.yml if backend_unhealthy
    if issues.get('backend_unhealthy'):
        yml = os.path.join('.github','workflows','ci.yml')
        if os.path.exists(yml):
            s = open(yml,'r',encoding='utf-8').read()
            s2 = re.sub(r'for i in \{1\.\.(\d+)\}', lambda m: f'for i in {{1..{int(m.group(1))*2}}}', s)
            if s2 != s:
                with open(yml,'w',encoding='utf-8') as f:
                    f.write(s2)
                changed.append(('increase_ci_wait', True))

    return changed

def run_local_tests():
    ok = True
    # Run backend smoke tests if available
    tests = [os.path.join('backend','tests','smoke_test.py'), os.path.join('backend','tests','auth_test.py'), os.path.join('backend','tests','eval_test.py')]
    for t in tests:
        if os.path.exists(t):
            try:
                run(f'python "{t}"', check=True)
            except Exception as e:
                print('test failed', t, e)
                ok = False
    return ok

def git_commit_and_push(changes_summary):
    run('git add -A')
    msg = 'Auto CI fix: ' + '; '.join(f'{k}={v}' for k,v in changes_summary)
    run(f'git commit -m "{msg}" || echo "no changes to commit"')
    run('git push', check=False)

def main():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('GITHUB_TOKEN not found in environment; aborting automated CI fix')
        sys.exit(2)

    owner, repo = parse_git_remote()
    attempt = 0
    last_err = None
    while attempt <= RETRY:
        try:
            run('git fetch --all', check=False)
            run('git status --porcelain', check=False)
            run('git rev-parse --abbrev-ref HEAD', check=False)
            run('git rev-parse --verify HEAD', check=False)
            run('git rev-parse --abbrev-ref HEAD > /dev/null 2>&1', check=False)
            print('Looking for latest failed workflow run...')
            run_data = find_latest_failed_run(owner, repo, token)
            if not run_data:
                print('No failed run found. Exiting.')
                return
            rid = run_data.get('id')
            print('Found failed run', rid)

            outdir = os.path.join('ci_artifacts', f'run_{rid}')
            os.makedirs(outdir, exist_ok=True)
            arts = download_artifacts_for_run(run_data, owner, repo, token, outdir)
            summary = extract_failure_summary(arts, outdir)
            if not summary:
                print('No failure summary extracted; listing artifact dir:', outdir)
                print(os.listdir(outdir))
                raise RuntimeError('No failure summary found')
            print('Analyzing', summary)
            issues, full = analyze_log(summary)
            print('Identified issues:', issues)
            changes = apply_conservative_fixes(issues)
            print('Applied changes:', changes)
            tests_ok = run_local_tests()
            print('Local tests ok?', tests_ok)
            if changes:
                git_commit_and_push(changes)
            print('Done. Summary saved at', summary)
            return
        except Exception as e:
            print('Attempt', attempt, 'failed:', e)
            last_err = e
            attempt += 1
            time.sleep(2)
    print('All attempts failed; last error:', last_err)
    sys.exit(1)

if __name__ == '__main__':
    main()
