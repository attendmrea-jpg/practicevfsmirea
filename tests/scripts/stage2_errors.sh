#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "=== ошибка во время исполнения стартового скрипта ==="
"$ROOT/run.sh" --script "$ROOT/tests/scripts/stage2_error.vsh" < /dev/null
echo "код возврата: $?"
echo "=== стартовый скрипт не найден ==="
"$ROOT/run.sh" --script "$ROOT/tests/scripts/nosuch.vsh" < /dev/null
echo "код возврата: $?"
