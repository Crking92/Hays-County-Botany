#!/usr/bin/env bash
set -euo pipefail

rm -rf dist
mkdir -p dist

cp index.html dist/
# Three public front doors share the same canonical plant-library assets.
cp field-id.html field-id-classic.html quiz.html quiz-classic.html dist/
# Public, source-credited photo booklet (no review-only media).
cp reed-lookalikes-field-guide.html dist/
test -s dist/reed-lookalikes-field-guide.html
test -s dist/field-id.html && test -s dist/field-id-classic.html && test -s dist/quiz.html && test -s dist/quiz-classic.html
# Publish only the current Photo Lab review; completed batches remain archived in GitHub.
cp photo-review.html dist/
if compgen -G "dist/photo-review-batch-*.html" >/dev/null; then
  echo "ERROR: old Photo Lab batch galleries must not appear on the public site" >&2
  exit 1
fi
cp _headers dist/
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
