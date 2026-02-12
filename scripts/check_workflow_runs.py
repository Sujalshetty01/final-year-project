#!/usr/bin/env python3
"""Check GitHub Actions workflow runs by ID (uses GITHUB_TOKEN if set)."""
import os, sys, json, urllib.request

def get_run(run_id, owner, repo, token=None):
    url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}'
    req = urllib.request.Request(url, headers={'User-Agent':'ci-checker'})
    if token:
        req.add_header('Authorization', f'token {token}')
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.load(resp)

def main():
    if len(sys.argv) < 4:
        print('usage: check_workflow_runs.py <owner> <repo> <run_id> [run_id ...]')
        sys.exit(2)
    owner = sys.argv[1]
    repo = sys.argv[2]
    run_ids = sys.argv[3:]
    token = os.environ.get('GITHUB_TOKEN')
    for rid in run_ids:
        try:
            r = get_run(rid, owner, repo, token)
            print(f"run={rid} name={r.get('name')} status={r.get('status')} conclusion={r.get('conclusion')} url={r.get('html_url')}")
        except Exception as e:
            print(f'error fetching run {rid}: {e}')

if __name__ == '__main__':
    main()
