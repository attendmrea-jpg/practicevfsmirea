#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUN="$ROOT/run.sh"
DATA="$ROOT/tests/data"
echo "=== порядок загрузки: пакет без зависимостей ==="
"$RUN" --package A --test-mode --repo-url "$DATA/single.graph" --order
echo "=== порядок загрузки: общая зависимость ==="
"$RUN" --package A --test-mode --repo-url "$DATA/simple.graph" --order
echo "=== порядок загрузки: три уровня вложенности ==="
"$RUN" --package A --test-mode --repo-url "$DATA/deep.graph" --order
echo "=== порядок загрузки: цикл в середине графа ==="
"$RUN" --package A --test-mode --repo-url "$DATA/inner_cycle.graph" --order
echo "=== порядок загрузки: весь граф в цикле ==="
"$RUN" --package A --test-mode --repo-url "$DATA/cycle.graph" --order
echo "=== порядок загрузки: реальный пакет ==="
"$RUN" --package serde_json --version 1.0.133 --order
echo "=== порядок загрузки: пакет с общими зависимостями ==="
"$RUN" --package syn --version 2.0.90 --order
