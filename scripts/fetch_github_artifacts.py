#!/usr/bin/env python3
import sys, os, json, urllib.request

def get_json(url, token=None):
    headers = {'User-Agent': 'ci-poller'}
    if token:
        headers['Authorization'] = f'token {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)

def download(url, outpath, token=None):
    headers = {'User-Agent': 'ci-poller'}
    if token:
        headers['Authorization'] = f'token {token}'
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
    with open(outpath, 'wb') as f:
        f.write(data)

def main():
    if len(sys.argv) < 4:
        print('usage: fetch_github_artifacts.py <run_id> <owner> <repo> [download(yes/no)]')
        sys.exit(2)
    run_id = sys.argv[1]
    owner = sys.argv[2]
    repo = sys.argv[3]
    do_download = (len(sys.argv) > 4 and sys.argv[4].lower().startswith('y'))
    token = os.environ.get('GITHUB_TOKEN')

    run_url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}'
    print('Fetching run metadata...')
    run = get_json(run_url, token)
    print('run id', run.get('id'), 'status', run.get('status'), 'conclusion', run.get('conclusion'))
    artifacts_url = run.get('artifacts_url')
    if not artifacts_url:
        print('No artifacts URL present')
        return
    print('Fetching artifacts list...')
    artifacts = get_json(artifacts_url, token)
    total = artifacts.get('total_count', 0)
    print('Artifacts total:', total)
    outdir = os.path.join('ci_artifacts', f'run_{run_id}')
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'artifacts.json'), 'w', encoding='utf-8') as f:
        json.dump(artifacts, f, indent=2)

    for a in artifacts.get('artifacts', []):
        aid = a.get('id')
        name = a.get('name')
        url = a.get('archive_download_url')
        print(aid, name, url)
        if do_download and url:
            outpath = os.path.join(outdir, f'artifact_{aid}_{name}.zip')
            try:
                print('  downloading to', outpath)
                download(url, outpath, token)
            except Exception as e:
                print('  download failed:', e)

    print('Saved artifacts metadata to', outdir)

if __name__ == '__main__':
    main()
