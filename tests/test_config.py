import os
import tempfile
import unittest

from src.cli import parse_args
from src.config import build_config, format_config
from src.errors import ConfigError

REAL_ARGS = ["--package", "serde", "--version", "1.0.200"]


def config_from(argv):
    return build_config(parse_args(argv))


class DefaultsTest(unittest.TestCase):
    def test_repo_url_has_default(self):
        config = config_from(REAL_ARGS)
        self.assertEqual(config.repo_url, "https://index.crates.io")

    def test_output_has_default(self):
        self.assertEqual(config_from(REAL_ARGS).output, "graph.svg")

    def test_test_mode_is_disabled_by_default(self):
        self.assertFalse(config_from(REAL_ARGS).test_mode)


class FormatTest(unittest.TestCase):
    def test_all_parameters_are_printed(self):
        text = format_config(config_from(REAL_ARGS))
        for key in ("package", "repo-url", "test-mode", "version", "output"):
            self.assertIn(key, text)

    def test_values_are_printed(self):
        text = format_config(config_from(REAL_ARGS))
        self.assertIn("= serde", text)
        self.assertIn("= 1.0.200", text)


class PackageErrorTest(unittest.TestCase):
    def test_missing_package(self):
        with self.assertRaises(ConfigError):
            config_from(["--version", "1.0.0"])

    def test_bad_package_name(self):
        with self.assertRaises(ConfigError):
            config_from(["--package", "a b", "--version", "1.0.0"])

    def test_test_package_must_be_uppercase(self):
        with self.assertRaises(ConfigError):
            config_from(["--package", "abc", "--test-mode",
                         "--repo-url", __file__])


class RepoErrorTest(unittest.TestCase):
    def test_url_scheme_is_required(self):
        with self.assertRaises(ConfigError):
            config_from(REAL_ARGS + ["--repo-url", "index.crates.io"])

    def test_missing_test_file(self):
        with self.assertRaises(ConfigError):
            config_from(["--package", "A", "--test-mode",
                         "--repo-url", "nosuchfile.txt"])

    def test_existing_test_file_is_accepted(self):
        config = config_from(["--package", "A", "--test-mode",
                              "--repo-url", __file__])
        self.assertTrue(config.test_mode)


class VersionErrorTest(unittest.TestCase):
    def test_missing_version(self):
        with self.assertRaises(ConfigError):
            config_from(["--package", "serde"])

    def test_bad_version(self):
        with self.assertRaises(ConfigError):
            config_from(["--package", "serde", "--version", "1.x"])

    def test_version_is_optional_in_test_mode(self):
        config = config_from(["--package", "A", "--test-mode",
                              "--repo-url", __file__])
        self.assertIsNone(config.version)


class OutputErrorTest(unittest.TestCase):
    def test_suffix_is_checked(self):
        with self.assertRaises(ConfigError):
            config_from(REAL_ARGS + ["--output", "graph.png"])

    def test_missing_directory(self):
        with self.assertRaises(ConfigError):
            config_from(REAL_ARGS + ["--output", "nosuchdir/graph.svg"])

    def test_existing_directory_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "graph.svg")
            self.assertEqual(config_from(REAL_ARGS +
                                         ["--output", path]).output, path)


if __name__ == "__main__":
    unittest.main()
