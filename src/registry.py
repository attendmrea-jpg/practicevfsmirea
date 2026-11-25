import json
import urllib.error
import urllib.request

from src.errors import RegistryError

USER_AGENT = "dependency-graph-visualizer (educational project)"
TIMEOUT_SECONDS = 30
NORMAL_KIND = "normal"
SHORT_NAME_LENGTH = 3
TINY_NAME_LENGTH = 2
PREFIX_LENGTH = 2


class Dependency:
    def __init__(self, name, requirement):
        self.name = name
        self.requirement = requirement

    def __repr__(self):
        return self.name + " " + self.requirement


class CratesIndex:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self._cache = {}

    def versions(self, package):
        key = package.lower()
        if key not in self._cache:
            self._cache[key] = parse_records(self._download(key), package)
        return self._cache[key]

    def direct_dependencies(self, package, version):
        record = self._find(package, version)
        return dependencies_of(record)

    def _find(self, package, version):
        for record in self.versions(package):
            if record.get("vers") == version:
                return record
        raise RegistryError(
            "версия не найдена в репозитории: " + package + " " + version
        )

    def _download(self, package):
        url = self.base_url + "/" + index_path(package)
        request = urllib.request.Request(
            url, headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(
                request, timeout=TIMEOUT_SECONDS
            ) as response:
                return response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            raise RegistryError(_http_message(package, error))
        except (urllib.error.URLError, OSError) as error:
            raise RegistryError("нет связи с репозиторием: " + str(error))


def index_path(package):
    name = package.lower()
    if len(name) <= TINY_NAME_LENGTH:
        return str(len(name)) + "/" + name
    if len(name) == SHORT_NAME_LENGTH:
        return str(SHORT_NAME_LENGTH) + "/" + name[0] + "/" + name
    return name[:PREFIX_LENGTH] + "/" + name[PREFIX_LENGTH:4] + "/" + name


def _http_message(package, error):
    if error.code == 404:
        return "пакет не найден в репозитории: " + package
    return "репозиторий ответил ошибкой " + str(error.code)


def parse_records(text, package):
    records = []
    for line in text.splitlines():
        if line.strip():
            records.append(parse_line(line, package))
    if not records:
        raise RegistryError("пустое описание пакета: " + package)
    return records


def parse_line(line, package):
    try:
        return json.loads(line)
    except ValueError as error:
        raise RegistryError(
            "неверный формат данных для " + package + ": " + str(error)
        )


def dependencies_of(record):
    found = {}
    for raw in record.get("deps", []):
        if is_required(raw):
            found[raw["name"]] = Dependency(raw["name"], raw.get("req", "*"))
    return [found[name] for name in sorted(found)]


def is_required(raw):
    return (
        raw.get("kind", NORMAL_KIND) == NORMAL_KIND
        and not raw.get("optional", False)
        and raw.get("target") is None
    )
