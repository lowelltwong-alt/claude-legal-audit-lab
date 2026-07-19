#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/upstream/claude-for-legal"
EXPECTED="5ceb305b30b4c82653c9b6642499c12e946ec319"
[[ -d "$DEST/.git" ]] || { echo "missing upstream checkout; run make bootstrap" >&2; exit 1; }
ACTUAL="$(git -C "$DEST" rev-parse HEAD)"
[[ "$ACTUAL" == "$EXPECTED" ]] || { echo "unexpected upstream HEAD: $ACTUAL" >&2; exit 1; }
if [[ -n "$(git -C "$DEST" status --porcelain)" ]]; then
  echo "upstream checkout has local modifications" >&2
  git -C "$DEST" status --short >&2
  exit 1
fi
echo "verified $ACTUAL"
