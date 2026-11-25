import os
import re

from src.errors import ConfigError

VERSION_PATTERN = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?$")
NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_\-]*$")
TEST_NAME_PATTERN = re.compile(r"^[A-Z]+$")
URL_SCHEMES = ("http://", "https://")
IMAGE_SUFFIX = ".svg"
ENABLED = "да"
DISABLED = "нет"
NOT_SET = "<не задано>"
FIELD_WIDTH = 9


class Config:
    def __init__(self, args):
        self.package = args.package
        self.repo_url = args.repo_url
        self.test_mode = args.test_mode
        self.version = args.version
        self.output = args.output
        self.direct = args.direct
        self.order = args.order

    def items(self):
        return [
            ("package", self.package),
            ("repo-url", self.repo_url),
            ("test-mode", ENABLED if self.test_mode else DISABLED),
            ("version", self.version or NOT_SET),
            ("output", self.output),
        ]


def build_config(args):
    config = Config(args)
    _check_package(config)
    _check_repo(config)
    _check_version(config)
    _check_output(config)
    return config


def format_config(config):
    lines = []
    for key, value in config.items():
        lines.append(key.ljust(FIELD_WIDTH) + " = " + str(value))
    return "\n".join(lines)


def _check_package(config):
    if not config.package:
        raise ConfigError("не задано имя пакета (--package)")
    if config.test_mode:
        _check_test_package(config.package)
    elif not NAME_PATTERN.match(config.package):
        raise ConfigError("недопустимое имя пакета: " + config.package)


def _check_test_package(name):
    if not TEST_NAME_PATTERN.match(name):
        raise ConfigError(
            "имя пакета тестового репозитория должно состоять "
            "из заглавных латинских букв: " + name
        )


def _check_repo(config):
    if not config.repo_url:
        raise ConfigError("не задан источник данных (--repo-url)")
    if config.test_mode:
        _check_test_repo(config.repo_url)
    elif not config.repo_url.startswith(URL_SCHEMES):
        raise ConfigError("URL репозитория: " + config.repo_url)


def _check_test_repo(path):
    if not os.path.isfile(path):
        raise ConfigError("файл тестового репозитория не найден: " + path)


def _check_version(config):
    if config.version is None:
        if config.test_mode:
            return
        raise ConfigError("не задана версия пакета (--version)")
    if not VERSION_PATTERN.match(config.version):
        raise ConfigError("недопустимая версия пакета: " + config.version)


def _check_output(config):
    if not config.output:
        raise ConfigError("не задано имя файла изображения (--output)")
    if not config.output.endswith(IMAGE_SUFFIX):
        raise ConfigError(
            "файл изображения должен иметь расширение "
            + IMAGE_SUFFIX + ": " + config.output
        )
    _check_output_dir(config.output)


def _check_output_dir(path):
    directory = os.path.dirname(os.path.abspath(path))
    if not os.path.isdir(directory):
        raise ConfigError("каталог для изображения не найден: " + directory)
