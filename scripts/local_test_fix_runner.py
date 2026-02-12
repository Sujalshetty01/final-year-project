#!/usr/bin/env python3
"""
Run backend tests locally, apply conservative fixes for common failures,
and re-run until tests pass (limited attempts). Commits and pushes minimal
changes (requirements updates) when fixes are applied.

Designed to run unattended and produce a final summary.
"""
import subprocess, sys, os, re, time

MAX_ATTEMPTS = 3
tests = [
    ('smoke', 'backend/tests/smoke_test.py', 'smoke_local.log'),
    ('auth', 'backend/tests/auth_test.py', 'auth_local.log'),
    ('eval', 'backend/tests/eval_test.py', 'eval_local.log'),
]

def run_cmd(cmd, cwd=None, capture=False):
    res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=capture, text=True)
    return res.returncode, res.stdout if capture else None, res.stderr if capture else None

def write_log(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)

def install_requirements():
    req = os.path.join('backend','requirements.txt')
    if os.path.exists(req):
        print('Installing backend requirements...')
        rc, out, err = run_cmd(f'python -m pip install --upgrade pip', capture=True)
        rc, out, err = run_cmd(f'pip install -r "{req}"', capture=True)
        print('pip install return', rc)
        return rc == 0
    return True

def kill_process_on_port(port):
    # Try to kill any process listening on the given TCP port (Windows-friendly)
    try:
        rc, out, err = run_cmd(f'netstat -ano | findstr ":{port}"', capture=True)
        if rc == 0 and out:
            # parse PIDs from netstat output lines
            pids = set()
            for line in out.splitlines():
                parts = [p for p in line.split() if p]
                if parts:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
            for pid in pids:
                run_cmd(f'taskkill /PID {pid} /F')
    except Exception:
        pass


def start_backend(timeout_seconds=20):
    # Start uvicorn in background and wait up to timeout_seconds for health
    log = 'backend-uvicorn.log'
    # allow overriding host/port/module/base via env vars for local debugging
    host = os.environ.get('BACKEND_HOST', '127.0.0.1')
    port = os.environ.get('BACKEND_PORT', '8000')
    module = os.environ.get('BACKEND_MODULE', 'app.main:app')

    # Kill any existing process on the port to avoid slow hangs
    try:
        kill_process_on_port(port)
    except Exception:
        pass

    # Launch uvicorn with the same Python interpreter (no reload, warning loglevel)
    popen = subprocess.Popen([sys.executable, '-m', 'uvicorn', module, '--host', host, '--port', str(port), '--log-level', 'warning'], stdout=open(log,'w'), stderr=subprocess.STDOUT, cwd=os.path.join(os.getcwd(),'backend'))

    # Determine base URL: if BACKEND_BASE_URL provided, use it as-is (it's expected to include /api/v1 if needed)
    import urllib.request
    ready = False
    base = os.environ.get('BACKEND_BASE_URL')
    if not base:
        base = f'http://{host}:{port}/api/v1'

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            # try ready and health endpoints (use base directly)
            req = urllib.request.Request(base + '/ready', headers={'User-Agent':'health-check'})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            pass
        try:
            req = urllib.request.Request(base + '/health', headers={'User-Agent':'health-check'})
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    ready = True
                    break
        except Exception:
            pass
        time.sleep(0.5)

    if not ready:
        # fail fast: kill process and return None
        try:
            stop_backend(popen)
        except Exception:
            pass
        print(f'ERROR: Backend did not become healthy within {timeout_seconds} seconds; see {log}')
        return None

    return popen

def stop_backend(popen):
    try:
        popen.terminate()
        popen.wait(timeout=5)
    except Exception:
        try:
            popen.kill()
        except Exception:
            pass

def analyze_log_for_missing_modules(text):
    mods = set()
    # ModuleNotFoundError: No module named 'xyz'
    for m in re.findall(r"ModuleNotFoundError: No module named ['\"]?([\w_\.\-]+)['\"]?", text):
        mods.add(m)
    for m in re.findall(r"No module named ['\"]?([\w_\.\-]+)['\"]?", text):
        mods.add(m)
    return list(mods)

def map_module_to_package(mod):
    # heuristic mappings for common mismatches
    m = mod.lower()
    if m == 'pydantic_settings' or m == 'pydantic-settings':
        return 'pydantic-settings'
    if m == 'uvicorn':
        return 'uvicorn'
    if m == 'fastapi':
        return 'fastapi'
    if m == 'prometheus_client':
        return 'prometheus-client'
    # default: use module name
    return mod

def attempt_fix_missing_packages(mods):
    added = []
    reqpath = os.path.join('backend','requirements.txt')
    existing = []
    if os.path.exists(reqpath):
        with open(reqpath,'r',encoding='utf-8') as f:
            existing = [l.strip().lower() for l in f if l.strip()]
    for m in mods:
        pkg = map_module_to_package(m)
        print('Attempting pip install', pkg)
        rc, out, err = run_cmd(f'pip install {pkg}', capture=True)
        if rc == 0:
            if os.path.exists(reqpath) and pkg.lower() not in existing:
                with open(reqpath,'a',encoding='utf-8') as f:
                    f.write('\n'+pkg)
                added.append(pkg)
        else:
            print('pip install failed for', pkg, 'err:', err)
    return added

def run_tests_and_collect(to_run):
    results = {}
    for name, script, logfile in tests:
        if name not in to_run:
            continue
        rc, out, err = run_cmd(f'"{sys.executable}" "{script}"', capture=True)
        # Only write logs when a test fails
        if rc != 0:
            combined = ''
            if out:
                combined += out
            if err:
                combined += '\n' + err
            write_log(logfile, combined)
            results[name] = {'rc': rc, 'log': logfile}
        else:
            results[name] = {'rc': rc, 'log': None}
    return results

def first_n_lines(path, n=200):
    if not os.path.exists(path):
        return ''
    with open(path,'r',encoding='utf-8',errors='ignore') as f:
        return '\n'.join([next(f).rstrip() for _ in range(n)])

def git_commit_and_push(message):
    run_cmd('git add -A')
    rc, out, err = run_cmd(f'git commit -m "{message}"', capture=True)
    if rc != 0:
        print('No commit made (perhaps no changes).')
        return False
    rc, out, err = run_cmd('git push', capture=True)
    print('git push rc', rc)
    return rc == 0

def main():
    summary = {'attempts': []}
    if not install_requirements():
        print('Failed to install requirements; continuing to tests anyway')

    attempt = 0
    to_run = [t[0] for t in tests]
    while attempt < MAX_ATTEMPTS and to_run:
        attempt += 1
        backend_proc = start_backend(timeout_seconds=20)
        if backend_proc is None:
            # failed to start; treat as global failure and attempt to analyze backend log
            summary['attempts'].append({'attempt': attempt, 'failures': to_run})
            # try to detect missing modules from backend log
            if os.path.exists('backend-uvicorn.log'):
                blast = open('backend-uvicorn.log','r',encoding='utf-8',errors='ignore').read()
                mods = analyze_log_for_missing_modules(blast)
                if mods:
                    added = attempt_fix_missing_packages(mods)
                    if added:
                        git_commit_and_push('Auto-fix: add missing requirements: ' + ','.join(added))
                        # re-run only the same tests after installing
                        to_run = to_run
                        continue
            # cannot proceed if backend won't start
            break

        # run only tests that remain to run
        res = run_tests_and_collect(to_run)
        # stop backend after tests
        stop_backend(backend_proc)

        # collect failing tests
        failing = [k for k,v in res.items() if v['rc'] != 0]
        summary['attempts'].append({'attempt': attempt, 'failures': failing})
        if not failing:
            summary['final'] = 'passed'
            break

        # analyze failures and attempt fixes
        for f in failing:
            logfile = res[f]['log']
            if logfile and os.path.exists(logfile):
                text = open(logfile,'r',encoding='utf-8',errors='ignore').read()
            else:
                text = ''
            mods = analyze_log_for_missing_modules(text)
            if mods:
                added = attempt_fix_missing_packages(mods)
                if added:
                    git_commit_and_push('Auto-fix: add missing requirements: ' + ','.join(added))
        # re-run only failed tests next attempt
        to_run = failing
        time.sleep(1)

    # final summary
    if summary.get('final') == 'passed':
        print('\nFINAL SUMMARY: Tests passed')
    else:
        print('\nFINAL SUMMARY: Tests did not pass after attempts')
    # print concise summary of attempts
    for a in summary['attempts']:
        print('Attempt', a['attempt'], 'failures:', a['failures'])

if __name__ == '__main__':
    main()
