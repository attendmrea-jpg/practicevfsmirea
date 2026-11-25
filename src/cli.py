import argparse

PROGRAM_INFO = "Визуализатор графа зависимостей пакетов Cargo"
PACKAGE_HELP = "имя анализируемого пакета"
REPO_HELP = "URL репозитория или путь к файлу тестового репозитория"
TEST_HELP = "режим работы с тестовым репозиторием"
VERSION_HELP = "версия пакета"
OUTPUT_HELP = "имя сгенерированного файла с изображением графа"
DIRECT_HELP = "вывести только прямые зависимости пакета"
ORDER_HELP = "вывести порядок загрузки зависимостей"
DEFAULT_REPO_URL = "https://index.crates.io"
DEFAULT_OUTPUT = "graph.svg"


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=PROGRAM_INFO)
    parser.add_argument("--package", help=PACKAGE_HELP)
    parser.add_argument(
        "--repo-url", dest="repo_url",
        default=DEFAULT_REPO_URL, help=REPO_HELP,
    )
    parser.add_argument(
        "--test-mode", dest="test_mode",
        action="store_true", help=TEST_HELP,
    )
    parser.add_argument("--version", help=VERSION_HELP)
    parser.add_argument(
        "--output", default=DEFAULT_OUTPUT, help=OUTPUT_HELP,
    )
    parser.add_argument(
        "--direct", action="store_true", help=DIRECT_HELP,
    )
    parser.add_argument(
        "--order", action="store_true", help=ORDER_HELP,
    )
    return parser.parse_args(argv)
