import re

from src.errors import RegistryError
from src.package import Package
from src.semver import parse_version, select

ARROW = "->"
COMMENT = "#"
SEPARATOR = ","
NAME_PATTERN = re.compile(r"^[A-Z]+$")


class RegistrySource:
    def __init__(self, index):
        self.index = index
        self._resolved = {}

    def direct(self, package):
        found = []
        for dependency in self._required(package):
            version = self._resolve(dependency)
            found.append(Package(dependency.name, version))
        return found

    def _required(self, package):
        return self.index.direct_dependencies(package.name, package.version)

    def _resolve(self, dependency):
        key = (dependency.name, dependency.requirement)
        if key not in self._resolved:
            self._resolved[key] = self._pick(dependency)
        return self._resolved[key]

    def _pick(self, dependency):
        available = self._available(dependency.name)
        chosen = select(available, dependency.requirement)
        if chosen is None:
            raise RegistryError(
                "не найдена версия " + dependency.name
                + " для требования " + dependency.requirement
            )
        return chosen.text

    def _available(self, name):
        versions = []
        for record in self.index.versions(name):
            if not record.get("yanked", False):
                versions.append(parse_version(record["vers"]))
        return versions


class TestSource:
    def __init__(self, table):
        self.table = table

    def direct(self, package):
        return [Package(name) for name in self.table.get(package.name, [])]

    def contains(self, name):
        return name in self.table


def load_test_repository(path):
    try:
        with open(path, encoding="utf-8") as stream:
            lines = stream.read().splitlines()
    except OSError as error:
        raise RegistryError("не удалось прочитать репозиторий: " + str(error))
    return _parse_table(lines, path)


def _parse_table(lines, path):
    table = {}
    for number, line in enumerate(lines, start=1):
        text = line.split(COMMENT)[0].strip()
        if text:
            name, children = _parse_line(text, number, path)
            table[name] = children
    if not table:
        raise RegistryError("тестовый репозиторий пуст: " + path)
    return table


def _parse_line(text, number, path):
    if ARROW not in text:
        raise _format_error(number, path)
    head, tail = text.split(ARROW, 1)
    name = _checked_name(head.strip(), number, path)
    children = []
    for part in tail.replace(SEPARATOR, " ").split():
        children.append(_checked_name(part, number, path))
    return name, children


def _checked_name(name, number, path):
    if not NAME_PATTERN.match(name):
        raise RegistryError(
            path + ": строка " + str(number) + ": имя пакета должно "
            "состоять из заглавных латинских букв: " + name
        )
    return name


def _format_error(number, path):
    return RegistryError(
        path + ": строка " + str(number) + ": ожидается запись вида "
        "\"A -> B, C\""
    )
