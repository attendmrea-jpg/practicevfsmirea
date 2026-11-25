import sys

from src import graph as graph_module
from src.cli import parse_args
from src.config import build_config, format_config
from src.errors import AppError, RegistryError
from src.package import Package
from src.registry import CratesIndex
from src.report import format_cycles, format_graph
from src.sources import RegistrySource, TestSource, load_test_repository

FAILURE_CODE = 1
ERROR_PREFIX = "ошибка: "
NO_DEPENDENCIES = "прямые зависимости отсутствуют"
INDENT = "  "


def main(argv=None):
    try:
        config = build_config(parse_args(argv))
        print(format_config(config))
        _run(config)
    except AppError as error:
        print(ERROR_PREFIX + str(error), file=sys.stderr)
        return FAILURE_CODE
    return 0


def _run(config):
    source, root = _prepare(config)
    if config.direct:
        _report_direct(source, root)
        return
    built = graph_module.build(source, root)
    print(format_graph(built))
    cycles = graph_module.find_cycles(built)
    if cycles:
        print(format_cycles(cycles))


def _prepare(config):
    if config.test_mode:
        return _test_source(config)
    index = CratesIndex(config.repo_url)
    return RegistrySource(index), Package(config.package, config.version)


def _test_source(config):
    table = load_test_repository(config.repo_url)
    source = TestSource(table)
    if not source.contains(config.package):
        raise RegistryError(
            "пакет не найден в тестовом репозитории: " + config.package
        )
    return source, Package(config.package)


def _report_direct(source, root):
    found = source.direct(root)
    print("прямые зависимости " + root.label + ":")
    if not found:
        print(INDENT + NO_DEPENDENCIES)
    for item in found:
        print(INDENT + item.label)


if __name__ == "__main__":
    sys.exit(main())
