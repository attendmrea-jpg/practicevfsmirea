#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VFS="$ROOT/tests/data/demo.zip"
SCRIPT="$ROOT/tests/scripts/stage2_basic.vsh"
echo "=== без параметров ==="
printf 'ls\ncd /tmp\nexit 0\n' | "$ROOT/run.sh"
echo "=== только --vfs ==="
printf 'ls\nexit 0\n' | "$ROOT/run.sh" --vfs "$VFS"
echo "=== только --script ==="
"$ROOT/run.sh" --script "$SCRIPT" < /dev/null
echo "=== оба параметра ==="
"$ROOT/run.sh" --vfs "$VFS" --script "$SCRIPT" < /dev/null
echo "код возврата: $?"
