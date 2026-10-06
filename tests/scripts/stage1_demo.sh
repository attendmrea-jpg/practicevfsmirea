#!/bin/sh
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
echo "=== демонстрация прототипа в интерактивном режиме ==="
"$ROOT/run.sh" <<'INPUT'
ls
ls -l /etc
cd /home/user
ls $HOME
ls $NOSUCHVARIABLE
nosuchcommand arg
cd a b
exit now
exit 0
INPUT
echo "код возврата: $?"
