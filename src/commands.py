"""Команды эмулятора."""
from src.errors import CommandError, ExitRequest

MAX_CD_ARGS = 1
MAX_EXIT_ARGS = 1


def cmd_ls(shell, args):
    """Заглушка: печатает имя команды и аргументы."""
    shell.write(" ".join(["ls"] + args))


def cmd_cd(shell, args):
    """Заглушка: печатает имя команды и аргументы."""
    if len(args) > MAX_CD_ARGS:
        raise CommandError("cd: слишком много аргументов")
    shell.write(" ".join(["cd"] + args))


def cmd_exit(shell, args):
    """Завершить работу эмулятора с необязательным кодом."""
    if len(args) > MAX_EXIT_ARGS:
        raise CommandError("exit: слишком много аргументов")
    raise ExitRequest(_exit_code(args))


def _exit_code(args):
    if not args:
        return 0
    try:
        return int(args[0])
    except ValueError:
        raise CommandError("exit: требуется числовой аргумент")


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
