"""Оболочка: приглашение, выполнение команд, цикл REPL."""
import getpass
import socket
import sys

from src.commands import COMMANDS
from src.errors import CommandError, EmulatorError
from src.parser import parse

PROMPT_SUFFIX = "$ "
ERROR_PREFIX = "ошибка: "
DEFAULT_VFS_NAME = "vfs"


class Shell:
    """Состояние эмулятора и обработка вводимых строк."""

    def __init__(self, output=None):
        self.output = output or sys.stdout
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".")[0]
        self.vfs_name = DEFAULT_VFS_NAME

    def prompt(self):
        """Приглашение к вводу вида user@host:имя_VFS$ ."""
        return "{}@{}:{}{}".format(
            self.user, self.host, self.vfs_name, PROMPT_SUFFIX
        )

    def write(self, text):
        """Вывести строку в поток вывода."""
        self.output.write(text + "\n")
        self.output.flush()

    def execute(self, line):
        """Разобрать и выполнить строку; ошибки пробрасываются."""
        name, args = parse(line)
        if name is None:
            return
        handler = COMMANDS.get(name)
        if handler is None:
            raise CommandError(name + ": команда не найдена")
        handler(self, args)

    def run_line(self, line):
        """Выполнить строку, сообщив об ошибке; вернуть успех."""
        try:
            self.execute(line)
        except EmulatorError as error:
            self.write(ERROR_PREFIX + str(error))
            return False
        return True

    def run(self):
        """Интерактивный цикл чтения и выполнения команд."""
        while True:
            try:
                line = input(self.prompt())
            except EOFError:
                self.write("")
                return
            self.run_line(line)
