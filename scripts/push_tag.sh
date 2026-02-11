#!/usr/bin/env bash
# Usage: ./scripts/push_tag.sh <remote-url> [branch]
set -euo pipefail
REMOTE_URL="$1"
BRANCH="${2:-main}"
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git init
  git add -A
  git commit -m "chore(review): initial commit for review" || true
fi
if ! git remote | grep -q origin; then
  git remote add origin "${REMOTE_URL}"
else
  git remote set-url origin "${REMOTE_URL}"
fi
git fetch origin || true
git push -u origin "${BRANCH}" || true
git push origin v1.0-first-review --force
echo "Pushed tag v1.0-first-review to ${REMOTE_URL}"
