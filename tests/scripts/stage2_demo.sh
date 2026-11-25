#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
RUN="$ROOT/run.sh"
echo "=== прямые зависимости rand 0.8.5 ==="
"$RUN" --package rand --version 0.8.5
echo "=== прямые зависимости regex 1.11.1 ==="
"$RUN" --package regex --version 1.11.1
echo "=== пакет без обязательных зависимостей ==="
"$RUN" --package serde --version 1.0.219
echo "=== ошибка: пакет не найден в репозитории ==="
"$RUN" --package nosuchcratehere --version 1.0.0
echo "код возврата: $?"
echo "=== ошибка: версия не найдена в репозитории ==="
"$RUN" --package rand --version 9.9.9
echo "код возврата: $?"
echo "=== ошибка: нет связи с репозиторием ==="
"$RUN" --package rand --version 0.8.5 --repo-url https://127.0.0.1:9
echo "код возврата: $?"
