#!/usr/bin/env python3
import sys
import time
import urllib.request
import json

if len(sys.argv) < 3:
    print('usage: .github_ci_poll.py <owner> <repo> [max_checks=30] [interval=10]')
    sys.exit(2)

owner = sys.argv[1]
repo = sys.argv[2]
max_checks = int(sys.argv[3]) if len(sys.argv) > 3 else 30
interval = int(sys.argv[4]) if len(sys.argv) > 4 else 10

url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=5'

last_id = None
for i in range(max_checks):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ci-poller'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
    except Exception as e:
        print(f'HTTP error: {e}')
        time.sleep(interval)
        continue

    runs = data.get('workflow_runs') or []
    if not runs:
        print('No workflow runs found yet.')
        time.sleep(interval)
        continue

    run = runs[0]
    rid = run.get('id')
    name = run.get('name') or run.get('path')
    status = run.get('status')
    conclusion = run.get('conclusion')
    html_url = run.get('html_url')
    head_branch = run.get('head_branch')
    head_sha = run.get('head_sha')

    if rid != last_id:
        print(f'Found run: id={rid} name={name} branch={head_branch} sha={head_sha} url={html_url}')
        last_id = rid

    print(f'  status={status} conclusion={conclusion}')

    if status == 'completed':
        print('\nWorkflow finished:')
        print(f'  id={rid} name={name} conclusion={conclusion} url={html_url}')
        if conclusion == 'success':
            sys.exit(0)
        else:
            sys.exit(3)

    time.sleep(interval)

print('Timed out waiting for workflow to complete')
sys.exit(4)
