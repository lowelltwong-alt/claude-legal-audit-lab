#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
find results -type f ! -name SHA256SUMS -print0 | sort -z | xargs -0 sha256sum > results/SHA256SUMS
