#!/usr/bin/env python3
"""
Auto-fix helper for CI failure summaries.
- Scans the generated failure summary for common error signatures
- Applies minimal fixes (add missing pip packages to backend/requirements.txt,
  increase health wait retries in CI) and commits/pushes using GITHUB_TOKEN

This script is intentionally conservative: it only appends package names
and increases wait counts by a bounded amount. It will not attempt risky
code changes.

Environment variables used:
- GITHUB_TOKEN: token provided to workflow (used to push commits)
- GITHUB_REPOSITORY: owner/repo
- GITHUB_ACTOR: actor name
- GITHUB_REF: branch ref

Usage:
  python .github/auto_fix.py --summary failure_summary_12345.txt --max-fixes 2

"""
from __future__ import annotations
import re
import sys
import os
from pathlib import Path
import subprocess
import argparse

PACKAGE_MAP = {
    'pydantic_settings': 'pydantic-settings',
    'jwt': 'PyJWT',
    'prometheus_client': 'prometheus_client',
    'slowapi': 'slowapi',
    'sklearn': 'scikit-learn',
    'matplotlib': 'matplotlib',
    'reportlab': 'reportlab',
    'torch': 'torch',
    'networkx': 'networkx',
}

CI_WORKFLOW_PATH = Path('.github/workflows/ci.yml')
REQS_PATH = Path('backend/requirements.txt')

GIT_AUTHOR_NAME = os.getenv('GITHUB_ACTOR', 'github-actions')
GIT_AUTHOR_EMAIL = f"{GIT_AUTHOR_NAME}@users.noreply.github.com"


def run(cmd, check=True, capture=False, env=None):
    if isinstance(cmd, (list, tuple)):
        proc = subprocess.run(cmd, check=check, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None, env=env)
        return proc.stdout.decode('utf-8') if capture else None
    else:
        proc = subprocess.run(cmd, shell=True, check=check, stdout=subprocess.PIPE if capture else None, stderr=subprocess.PIPE if capture else None, env=env)
        return proc.stdout.decode('utf-8') if capture else None


def find_missing_modules(text: str) -> set[str]:
    # Match patterns like: ModuleNotFoundError: No module named 'xyz'
    mods = set(re.findall(r"No module named '([A-Za-z0-9_]+)'", text))
    return mods


def append_requirements(pkgs: list[str]) -> bool:
    if not REQS_PATH.exists():
        REQS_PATH.parent.mkdir(parents=True, exist_ok=True)
        REQS_PATH.write_text('')
    before = REQS_PATH.read_text().splitlines()
    added = []
    for p in pkgs:
        if p not in before and p not in added:
            added.append(p)
    if not added:
        return False
    with REQS_PATH.open('a', encoding='utf-8') as fh:
        for p in added:
            fh.write('\n' + p)
    print('Appended requirements:', added)
    return True


def increase_wait_retries(summary_text: str, inc: int = 60) -> bool:
    # Look for the health wait loop in CI workflow and increase upper bound
    if not CI_WORKFLOW_PATH.exists():
        return False
    text = CI_WORKFLOW_PATH.read_text()
    m = re.search(r"for i in \{1\.\.([0-9]+)\}; do", text)
    if not m:
        return False
    cur = int(m.group(1))
    new = cur + inc
    new_text = re.sub(r"for i in \{1\.\.([0-9]+)\}; do", f"for i in {{1..{new}}}; do", text)
    CI_WORKFLOW_PATH.write_text(new_text)
    print(f'Increased CI wait retries from {cur} to {new}')
    return True


def git_commit_and_push(files: list[str], message: str) -> bool:
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPOSITORY')
    ref = os.getenv('GITHUB_REF', 'refs/heads/master')
    if not token or not repo:
        print('Missing GITHUB_TOKEN or GITHUB_REPOSITORY; cannot push')
        return False
    branch = ref.split('/')[-1]
    # configure git
    run(['git', 'config', 'user.name', GIT_AUTHOR_NAME])
    run(['git', 'config', 'user.email', GIT_AUTHOR_EMAIL])
    run(['git', 'add'] + files)
    run(['git', 'commit', '-m', message])
    # set remote with token
    url = f'https://x-access-token:{token}@github.com/{repo}.git'
    run(['git', 'remote', 'set-url', 'origin', url])
    try:
        run(['git', 'push', 'origin', branch])
        print('Pushed commit to', branch)
        return True
    except Exception as e:
        print('Failed to push commit:', e)
        return False


def count_prior_autofix_commits() -> int:
    try:
        out = run(['git', 'log', '--pretty=%s', '-n', '50'], check=True, capture=True)
    except Exception:
        return 0
    return sum(1 for line in out.splitlines() if line.startswith('ci(auto-fix):'))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--summary', required=True)
    p.add_argument('--max-fixes', type=int, default=2)
    args = p.parse_args()

    if not Path(args.summary).exists():
        print('Summary not found:', args.summary)
        sys.exit(0)

    summary = Path(args.summary).read_text(encoding='utf-8', errors='ignore')

    # Limit number of auto-fix attempts
    prior = count_prior_autofix_commits()
    print('Prior auto-fix commits in recent history:', prior)
    if prior >= args.max_fixes:
        print('Max auto-fix attempts reached; aborting auto-fix')
        sys.exit(0)

    made_changes = False

    # 1) Missing modules -> add to backend/requirements.txt
    mods = find_missing_modules(summary)
    if mods:
        pkgs = []
        for m in mods:
            if m in PACKAGE_MAP:
                pkgs.append(PACKAGE_MAP[m])
            else:
                # default to same name (best-effort)
                pkgs.append(m)
        if append_requirements(pkgs):
            made_changes = True

    # 2) Health probe failures -> increase wait retries modestly
    if 'backend did not become healthy' in summary or 'backend did not become healthy' in summary.lower():
        if increase_wait_retries(summary, inc=60):
            made_changes = True

    if made_changes:
        files = []
        if REQS_PATH.exists():
            files.append(str(REQS_PATH))
        if CI_WORKFLOW_PATH.exists():
            files.append(str(CI_WORKFLOW_PATH))
        if not files:
            print('No files changed to commit')
            sys.exit(0)
        msg = 'ci(auto-fix): ' + ','.join(os.path.basename(f) for f in files)
        ok = git_commit_and_push(files, msg)
        if not ok:
            sys.exit(1)
        print('Auto-fix committed; a new workflow run will be triggered by this push')
    else:
        print('No auto-fixable issues detected in summary')


if __name__ == '__main__':
    main()
