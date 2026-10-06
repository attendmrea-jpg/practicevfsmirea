"""Разбор строки команды и раскрытие переменных окружения."""
import os

VAR_PREFIX = "$"
NAME_EXTRA = "_"


def parse(line):
    """Разделить строку на команду и аргументы, раскрыв $VAR."""
    words = [_expand(word) for word in line.split()]
    if not words:
        return None, []
    return words[0], words[1:]


def _expand(word):
    parts = []
    index = 0
    while index < len(word):
        char = word[index]
        if char != VAR_PREFIX:
            parts.append(char)
            index += 1
            continue
        name, index = _read_name(word, index + 1)
        parts.append(VAR_PREFIX if name is None else _value_of(name))
    return "".join(parts)


def _read_name(word, start):
    end = start
    while end < len(word) and _is_name_char(word[end]):
        end += 1
    if end == start:
        return None, start
    return word[start:end], end


def _is_name_char(char):
    return char.isalnum() or char in NAME_EXTRA


def _value_of(name):
    return os.environ.get(name, "")
