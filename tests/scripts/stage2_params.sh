#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$(mktemp -d)"
python3 -I "$ROOT/tests/tools/make_vfs.py" "$WORK"
VFS="$WORK/vfs_files.zip"
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
rm -rf "$WORK"
