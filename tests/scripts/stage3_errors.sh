#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WORK="$(mktemp -d)"
printf 'не zip-архив\n' > "$WORK/broken.zip"
echo "=== образ VFS не найден ==="
"$ROOT/run.sh" --vfs "$WORK/nosuch.zip" < /dev/null
echo "код возврата: $?"
echo "=== неверный формат образа VFS ==="
"$ROOT/run.sh" --vfs "$WORK/broken.zip" < /dev/null
echo "код возврата: $?"
echo "=== ошибки команд при работе с VFS ==="
python3 -I "$ROOT/tests/tools/make_vfs.py" "$WORK"
printf 'nosuchcommand\ncd a b\nexit now\nexit 0\n' |
    "$ROOT/run.sh" --vfs "$WORK/vfs_deep.zip"
echo "=== vfs-init перезаписывает физический образ ==="
echo "размер образа до: $(wc -c < "$WORK/vfs_deep.zip") байт"
printf 'vfs-init\nvfs-init arg\n' | "$ROOT/run.sh" --vfs "$WORK/vfs_deep.zip"
echo "размер образа после: $(wc -c < "$WORK/vfs_deep.zip") байт"
rm -rf "$WORK"
