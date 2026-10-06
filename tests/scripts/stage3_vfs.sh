#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/tests/scripts/stage3_all.vsh"
WORK="$(mktemp -d)"
python3 -I "$ROOT/tests/tools/make_vfs.py" "$WORK"
for name in vfs_min vfs_files vfs_deep; do
    echo "=== VFS: $name ==="
    "$ROOT/run.sh" --vfs "$WORK/$name.zip" --script "$SCRIPT" < /dev/null
done
rm -rf "$WORK"
