#!/usr/bin/env bash
set -euo pipefail

rm -rf dist
mkdir -p dist

cp index.html dist/
cp manifest.webmanifest dist/
cp sw.js dist/

cp -R assets dist/assets
cp -R content dist/content
cp -R data dist/data

echo "Hays Botany static site staged in ./dist"
find dist -type f | wc -l | xargs echo "Files staged:"
