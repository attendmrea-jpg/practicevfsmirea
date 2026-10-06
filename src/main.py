"""Точка входа эмулятора."""
import argparse
import sys

from src.errors import EmulatorError, ExitRequest
from src.shell import ERROR_PREFIX, Shell

FAILURE_CODE = 1
PROGRAM_INFO = "Эмулятор командной оболочки UNIX-подобной ОС"
VFS_HELP = "путь к физическому расположению VFS"
SCRIPT_HELP = "путь к стартовому скрипту"


def main(argv=None):
    """Запустить эмулятор и вернуть код завершения."""
    args = _parse_args(argv)
    shell = Shell(vfs_path=args.vfs_path, script_path=args.script_path)
    shell.write_debug()
    try:
        _start(shell)
    except ExitRequest as request:
        return request.code
    except EmulatorError as error:
        shell.write(ERROR_PREFIX + str(error))
        return FAILURE_CODE
    return 0


def _start(shell):
    shell.load_vfs()
    if shell.script_path:
        shell.run_script(shell.script_path)
    shell.run()


def _parse_args(argv):
    parser = argparse.ArgumentParser(description=PROGRAM_INFO)
    parser.add_argument("--vfs", dest="vfs_path", help=VFS_HELP)
    parser.add_argument("--script", dest="script_path", help=SCRIPT_HELP)
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
