import sys

from src.cli import parse_args
from src.config import build_config, format_config
from src.errors import AppError
from src.registry import CratesIndex

FAILURE_CODE = 1
ERROR_PREFIX = "ошибка: "
NO_DEPENDENCIES = "прямые зависимости отсутствуют"
INDENT = "  "


def main(argv=None):
    try:
        config = build_config(parse_args(argv))
        print(format_config(config))
        _report_direct(config)
    except AppError as error:
        print(ERROR_PREFIX + str(error), file=sys.stderr)
        return FAILURE_CODE
    return 0


def _report_direct(config):
    if config.test_mode:
        return
    index = CratesIndex(config.repo_url)
    found = index.direct_dependencies(config.package, config.version)
    print(_title(config))
    if not found:
        print(INDENT + NO_DEPENDENCIES)
    for dependency in found:
        print(INDENT + dependency.name + " " + dependency.requirement)


def _title(config):
    return "прямые зависимости " + config.package + " " + config.version + ":"


if __name__ == "__main__":
    sys.exit(main())
