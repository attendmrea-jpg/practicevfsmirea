"""Точка входа эмулятора."""
import sys

from src.errors import ExitRequest
from src.shell import Shell


def main():
    """Запустить REPL и вернуть код завершения."""
    shell = Shell()
    try:
        shell.run()
    except ExitRequest as request:
        return request.code
    return 0


if __name__ == "__main__":
    sys.exit(main())
