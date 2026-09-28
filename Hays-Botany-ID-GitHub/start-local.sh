#!/usr/bin/env sh
set -eu

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js 22 is required: https://nodejs.org/"
  exit 1
fi

if [ ! -d node_modules ]; then
  npm ci
fi

npm run dev
