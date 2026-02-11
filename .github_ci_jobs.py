#!/usr/bin/env python3
import sys
import urllib.request
import json

if len(sys.argv) < 4:
    print('usage: .github_ci_jobs.py <owner> <repo> <run_id>')
    sys.exit(2)

owner = sys.argv[1]
repo = sys.argv[2]
run_id = sys.argv[3]

url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/jobs'
req = urllib.request.Request(url, headers={'User-Agent': 'ci-job-fetcher'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.load(resp)
except Exception as e:
    print('Failed to fetch jobs:', e)
    sys.exit(3)

jobs = data.get('jobs', [])
if not jobs:
    print('No jobs found for run', run_id)
    sys.exit(0)

for job in jobs:
    jid = job.get('id')
    name = job.get('name')
    status = job.get('status')
    conclusion = job.get('conclusion')
    print(f'JOB id={jid} name={name} status={status} conclusion={conclusion}')
    steps = job.get('steps') or []
    for step in steps:
        sname = step.get('name')
        sstatus = step.get('status')
        sconcl = step.get('conclusion')
        print(f'  STEP: {sname} status={sstatus} conclusion={sconcl}')
    print('  logs_url:', job.get('logs_url'))
    print()

# Summarize failures
failed_jobs = [j for j in jobs if j.get('conclusion') != 'success']
if not failed_jobs:
    print('All jobs succeeded')
    sys.exit(0)

print('Failed jobs:')
for j in failed_jobs:
    print(' -', j.get('name'), 'conclusion=', j.get('conclusion'))

sys.exit(1)
