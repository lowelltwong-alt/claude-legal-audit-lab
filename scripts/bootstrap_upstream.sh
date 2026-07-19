#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/upstream/claude-for-legal"
REPO="https://github.com/anthropics/claude-for-legal.git"
COMMIT="5ceb305b30b4c82653c9b6642499c12e946ec319"

if [[ -d "$DEST/.git" ]]; then
  actual="$(git -C "$DEST" rev-parse HEAD)"
  if [[ "$actual" == "$COMMIT" ]]; then
    echo "upstream already pinned: $actual"
    exit 0
  fi
  echo "refusing to overwrite unexpected checkout at $DEST (HEAD=$actual)" >&2
  exit 1
fi

mkdir -p "$(dirname "$DEST")"
git clone --no-tags "$REPO" "$DEST"
git -C "$DEST" checkout --detach "$COMMIT"
actual="$(git -C "$DEST" rev-parse HEAD)"
[[ "$actual" == "$COMMIT" ]] || { echo "commit verification failed: $actual" >&2; exit 1; }
echo "pinned upstream checkout: $actual"
