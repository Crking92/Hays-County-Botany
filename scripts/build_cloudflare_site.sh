#!/usr/bin/env bash
set -euo pipefail

rm -rf dist
mkdir -p dist

cp index.html dist/
cp photo-review*.html dist/  # Photo Lab batches each publish their own standalone page
cp manifest.webmanifest dist/
cp sw.js dist/

# Photo Lab is a real standalone route. Without this file, Cloudflare's
# single-page-app fallback silently renders the learner homepage instead.
test -s dist/photo-review.html
if cmp -s dist/photo-review.html dist/index.html; then
  echo "ERROR: Photo Lab route accidentally contains the homepage" >&2
  exit 1
fi

cp -R assets dist/assets
cp -R content dist/content
cp -R data dist/data

echo "Hays Botany static site staged in ./dist"
find dist -type f | wc -l | xargs echo "Files staged:"
