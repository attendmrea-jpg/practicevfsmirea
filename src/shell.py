"""Оболочка: приглашение, выполнение команд, цикл REPL."""
import getpass
import os
import socket
import sys

from src.commands import COMMANDS
from src.errors import CommandError, EmulatorError, ScriptError
from src.parser import parse

PROMPT_SUFFIX = "$ "
ERROR_PREFIX = "ошибка: "
DEFAULT_VFS_NAME = "vfs"
DEBUG_PREFIX = "[debug] "
NOT_SET = "<не задан>"


class Shell:
    """Состояние эмулятора и обработка вводимых строк."""

    def __init__(self, vfs_path=None, script_path=None, output=None):
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.output = output or sys.stdout
        self.user = getpass.getuser()
        self.host = socket.gethostname().split(".")[0]
        self.vfs_name = _name_of(vfs_path)

    def prompt(self):
        """Приглашение к вводу вида user@host:имя_VFS$ ."""
        return "{}@{}:{}{}".format(
            self.user, self.host, self.vfs_name, PROMPT_SUFFIX
        )

    def write(self, text):
        """Вывести строку в поток вывода."""
        self.output.write(text + "\n")
        self.output.flush()

    def write_debug(self):
        """Отладочный вывод всех заданных параметров запуска."""
        self.write(DEBUG_PREFIX + "vfs    = " + _shown(self.vfs_path))
        self.write(DEBUG_PREFIX + "script = " + _shown(self.script_path))

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

    def run_script(self, path):
        """Выполнить стартовый скрипт до первой ошибки.

        Ввод и вывод отображаются как диалог с пользователем.
        """
        for number, line in _read_script(path):
            self.write(self.prompt() + line)
            if not self.run_line(line):
                raise ScriptError(
                    "{}: строка {}: выполнение остановлено".format(
                        path, number
                    )
                )

    def run(self):
        """Интерактивный цикл чтения и выполнения команд."""
        while True:
            try:
                line = input(self.prompt())
            except EOFError:
                self.write("")
                return
            self.run_line(line)


def _read_script(path):
    try:
        with open(path, encoding="utf-8") as stream:
            lines = stream.read().splitlines()
    except OSError as error:
        raise ScriptError("не удалось прочитать скрипт: " + str(error))
    return [
        (number, line.strip())
        for number, line in enumerate(lines, start=1)
        if line.strip()
    ]


def _shown(value):
    return value if value else NOT_SET


def _name_of(vfs_path):
    if not vfs_path:
        return DEFAULT_VFS_NAME
    return os.path.splitext(os.path.basename(vfs_path))[0]
