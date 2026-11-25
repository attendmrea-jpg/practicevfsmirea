import sys

from src.cli import parse_args
from src.config import build_config, format_config
from src.errors import AppError

FAILURE_CODE = 1
ERROR_PREFIX = "ошибка: "


def main(argv=None):
    try:
        config = build_config(parse_args(argv))
    except AppError as error:
        print(ERROR_PREFIX + str(error), file=sys.stderr)
        return FAILURE_CODE
    print(format_config(config))
    return 0


if __name__ == "__main__":
    sys.exit(main())
