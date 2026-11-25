#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUN="$ROOT/run.sh"
echo "=== вывод всех настраиваемых параметров ==="
"$RUN" --package serde --version 1.0.219 --output graph.svg
echo "=== параметры тестового репозитория ==="
"$RUN" --package A --test-mode \
    --repo-url "$ROOT/tests/data/simple.graph" --output graph.svg
echo "=== ошибка: не задано имя пакета ==="
"$RUN" --version 1.0.219
echo "код возврата: $?"
echo "=== ошибка: недопустимое имя пакета ==="
"$RUN" --package "bad name" --version 1.0.219
echo "код возврата: $?"
echo "=== ошибка: имя пакета не заглавными буквами ==="
"$RUN" --package abc --test-mode --repo-url "$ROOT/tests/data/simple.graph"
echo "код возврата: $?"
echo "=== ошибка: неверный URL репозитория ==="
"$RUN" --package serde --version 1.0.219 --repo-url index.crates.io
echo "код возврата: $?"
echo "=== ошибка: файл тестового репозитория не найден ==="
"$RUN" --package A --test-mode --repo-url nosuchfile.graph
echo "код возврата: $?"
echo "=== ошибка: не задана версия пакета ==="
"$RUN" --package serde
echo "код возврата: $?"
echo "=== ошибка: недопустимая версия пакета ==="
"$RUN" --package serde --version 1.x
echo "код возврата: $?"
echo "=== ошибка: неверное расширение файла изображения ==="
"$RUN" --package serde --version 1.0.219 --output graph.png
echo "код возврата: $?"
echo "=== ошибка: каталог для изображения не найден ==="
"$RUN" --package serde --version 1.0.219 --output nosuchdir/graph.svg
echo "код возврата: $?"
