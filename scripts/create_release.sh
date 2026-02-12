#!/usr/bin/env bash
set -euo pipefail

# Package common release artifacts into a zip and print gh CLI example to publish.
OUT=release-artifacts
mkdir -p "$OUT"

# Copy selected artifacts if they exist
[ -f paper/ieee_paper_main.pdf ] && cp paper/ieee_paper_main.pdf "$OUT/"
[ -f paper/build.log ] && cp paper/build.log "$OUT/"
[ -d docs ] && cp -r docs "$OUT/"

ZIP=release-v1.0.0.zip
zip -r "$ZIP" "$OUT"

echo "Created $ZIP with artifacts."
echo "To publish via gh CLI (authenticated):"
echo "  gh release create v1.0.0 --title 'v1.0.0' --notes-file RELEASE_DRAFT.md $ZIP"
