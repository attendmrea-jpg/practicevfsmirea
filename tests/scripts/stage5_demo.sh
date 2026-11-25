#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUN="$ROOT/run.sh"
OUT="$(mktemp -d)"
echo "=== визуализация: syn 2.0.90 ==="
"$RUN" --package syn --version 2.0.90 --output "$OUT/syn.svg"
echo "=== визуализация: serde_json 1.0.133 ==="
"$RUN" --package serde_json --version 1.0.133 --output "$OUT/serde_json.svg"
echo "=== визуализация: reqwest 0.12.9 ==="
"$RUN" --package reqwest --version 0.12.9 --output "$OUT/reqwest.svg" |
    tail -3
echo "=== визуализация: тестовый репозиторий с циклом ==="
"$RUN" --package A --test-mode --repo-url "$ROOT/tests/data/cycle.graph" \
    --output "$OUT/cycle.svg"
echo "=== созданные файлы ==="
ls -1 "$OUT"
rm -rf "$OUT"
