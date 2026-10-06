"""Исключения эмулятора."""


class EmulatorError(Exception):
    """Базовая ошибка эмулятора, выводимая пользователю."""


class CommandError(EmulatorError):
    """Неизвестная команда или неверные аргументы."""


class ScriptError(EmulatorError):
    """Ошибка чтения или выполнения стартового скрипта."""


class VfsError(EmulatorError):
    """Ошибка загрузки или разбора образа VFS."""


class ExitRequest(Exception):
    """Запрос на завершение работы эмулятора."""

    def __init__(self, code=0):
        super().__init__(code)
        self.code = code
