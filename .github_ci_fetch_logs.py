#!/usr/bin/env python3
import sys
import urllib.request
import json
import os
import io
import zipfile

if len(sys.argv) < 4:
    print('usage: .github_ci_fetch_logs.py <owner> <repo> <run_id>')
    sys.exit(2)

owner = sys.argv[1]
repo = sys.argv[2]
run_id = sys.argv[3]

url = f'https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/logs'
print('Fetching logs from', url)
headers = {'User-Agent': 'ci-log-fetcher'}
token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
if token:
    headers['Authorization'] = f'token {token}'
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()
except urllib.error.HTTPError as e:
    print('Failed to download logs: HTTP', e.code)
    try:
        print(e.read().decode())
    except Exception:
        pass
    sys.exit(3)
except Exception as e:
    print('Failed to download logs:', e)
    sys.exit(3)

outzip = f'run_{run_id}_logs.zip'
with open(outzip, 'wb') as f:
    f.write(data)
print('Saved logs to', outzip)

# unzip to folder
outdir = f'run_{run_id}_logs'
os.makedirs(outdir, exist_ok=True)
with zipfile.ZipFile(outzip, 'r') as z:
    z.extractall(outdir)
print('Extracted logs to', outdir)

# find files and search for errors
candidates = []
for root, dirs, files in os.walk(outdir):
    for fn in files:
        path = os.path.join(root, fn)
        # only text files
        if fn.endswith('.txt') or fn.endswith('.log') or True:
            candidates.append(path)

# Also include local log files that the workflow may have written
local_logs = [
    'backend-build.log',
    'frontend-build.log',
    'backend-uvicorn.log',
    'backend-inspect.json',
    'smoke.log',
    'auth.log',
    'eval.log',
]
for lf in local_logs:
    if os.path.exists(lf):
        candidates.append(os.path.abspath(lf))

matches = []
for p in candidates:
    try:
        with open(p, 'r', errors='ignore') as f:
            txt = f.read()
    except Exception:
        continue
    # look for common failure markers
    if ('Traceback' in txt) or ('FAIL' in txt) or ('ERROR' in txt) or ('AssertionError' in txt) or ('failed' in txt.lower()):
        matches.append((p, txt))

# Build a concise failure summary
summary_lines = []
summary_lines.append(f'Workflow run: {owner}/{repo} run_id={run_id}')
summary_lines.append(f'Files scanned: {len(candidates)}')
summary_lines.append(f'Files with failure markers: {len(matches)}')

if matches:
    # list top 10 files with markers
    summary_lines.append('\nTop files with markers:')
    for p, txt in matches[:10]:
        # find first marker in the file
        first_marker = None
        for marker in ('Traceback', 'ERROR', 'FAIL', 'AssertionError', 'failed'):
            if marker in txt:
                first_marker = marker
                break
        summary_lines.append(f'- {p} (marker={first_marker})')

    # extract first useful snippet for root cause
    first_snippet = None
    for p, txt in matches:
        if 'Traceback' in txt:
            idx = txt.find('Traceback')
            start = max(0, idx - 200)
            end = min(len(txt), idx + 1000)
            first_snippet = txt[start:end]
            snippet_source = p
            break
    if not first_snippet:
        # fallback to ERROR or FAIL snippet
        for p, txt in matches:
            for marker in ('ERROR', 'FAIL', 'AssertionError'):
                if marker in txt:
                    idx = txt.find(marker)
                    start = max(0, idx - 200)
                    end = min(len(txt), idx + 800)
                    first_snippet = txt[start:end]
                    snippet_source = p
                    break
            if first_snippet:
                break

    if first_snippet:
        summary_lines.append('\n--- Root cause snippet from: ' + snippet_source + ' ---')
        # include only first 20 lines of snippet
        snippet_lines = first_snippet.strip().splitlines()
        for ln in snippet_lines[:20]:
            summary_lines.append(ln)
    else:
        summary_lines.append('\nNo detailed snippet available.')
else:
    summary_lines.append('\nNo failure markers found in logs.')

# write summary to file
summary_path = f'failure_summary_{run_id}.txt'
with open(summary_path, 'w', encoding='utf-8') as sf:
    sf.write('\n'.join(summary_lines))

print('\n'.join(summary_lines))

print(f'Wrote failure summary to {summary_path}')

if not matches:
    print('No obvious error markers found. Showing tails of job logs:')
    for p in candidates:
        try:
            with open(p, 'r', errors='ignore') as f:
                lines = f.readlines()
        except Exception:
            continue
        if not lines:
            continue
        print('\n---', p, '---')
        for line in lines[-200:]:
            print(line.rstrip())
else:
    print(f'Found {len(matches)} files with error markers. Showing snippets:')
    for p, txt in matches:
        print('\n===', p, '===')
        # print surrounding context around first match
        for marker in ('Traceback', 'ERROR', 'FAIL', 'AssertionError', 'failed'):
            if marker in txt:
                idx = txt.find(marker)
                start = max(0, idx-400)
                end = min(len(txt), idx+800)
                snippet = txt[start:end]
                print(snippet)
                break

print('\nDone.')
sys.exit(0)
