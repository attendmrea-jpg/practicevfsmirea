import io
import json
import unittest
import urllib.error
from unittest import mock

from src.errors import RegistryError
from src.registry import (
    CratesIndex,
    dependencies_of,
    index_path,
    parse_records,
)

RECORDS = [
    {"name": "demo", "vers": "0.1.0", "deps": []},
    {"name": "demo", "vers": "1.2.3", "deps": [
        {"name": "libc", "req": "^0.2", "kind": "normal",
         "optional": False, "target": None},
        {"name": "serde", "req": "^1.0", "kind": "normal",
         "optional": True, "target": None},
        {"name": "criterion", "req": "^0.5", "kind": "dev",
         "optional": False, "target": None},
        {"name": "winapi", "req": "^0.3", "kind": "normal",
         "optional": False, "target": "cfg(windows)"},
    ]},
]


def index_text():
    return "\n".join(json.dumps(record) for record in RECORDS)


def fake_response(text):
    response = mock.MagicMock()
    response.read.return_value = text.encode("utf-8")
    response.__enter__.return_value = response
    return response


def index_with(text):
    index = CratesIndex("https://index.crates.io")
    patcher = mock.patch(
        "urllib.request.urlopen", return_value=fake_response(text)
    )
    patcher.start()
    return index, patcher


class IndexPathTest(unittest.TestCase):
    def test_one_letter(self):
        self.assertEqual(index_path("a"), "1/a")

    def test_two_letters(self):
        self.assertEqual(index_path("ab"), "2/ab")

    def test_three_letters(self):
        self.assertEqual(index_path("abc"), "3/a/abc")

    def test_long_name(self):
        self.assertEqual(index_path("serde"), "se/rd/serde")

    def test_name_is_lowercased(self):
        self.assertEqual(index_path("Serde"), "se/rd/serde")


class ParseTest(unittest.TestCase):
    def test_records_are_parsed(self):
        self.assertEqual(len(parse_records(index_text(), "demo")), 2)

    def test_blank_lines_are_skipped(self):
        text = index_text() + "\n\n"
        self.assertEqual(len(parse_records(text, "demo")), 2)

    def test_broken_json(self):
        with self.assertRaises(RegistryError):
            parse_records("{not json", "demo")

    def test_empty_answer(self):
        with self.assertRaises(RegistryError):
            parse_records("   ", "demo")


class DependenciesTest(unittest.TestCase):
    def test_only_required_normal_dependencies(self):
        found = dependencies_of(RECORDS[1])
        self.assertEqual([item.name for item in found], ["libc"])

    def test_requirement_is_kept(self):
        self.assertEqual(dependencies_of(RECORDS[1])[0].requirement, "^0.2")

    def test_package_without_dependencies(self):
        self.assertEqual(dependencies_of(RECORDS[0]), [])


class DownloadTest(unittest.TestCase):
    def setUp(self):
        self.index, self.patcher = index_with(index_text())
        self.addCleanup(self.patcher.stop)

    def test_dependencies_of_version(self):
        found = self.index.direct_dependencies("demo", "1.2.3")
        self.assertEqual([item.name for item in found], ["libc"])

    def test_unknown_version(self):
        with self.assertRaises(RegistryError):
            self.index.direct_dependencies("demo", "9.9.9")

    def test_answer_is_cached(self):
        self.index.versions("demo")
        self.index.versions("demo")
        self.assertEqual(len(self.index.versions("demo")), 2)


class HttpErrorTest(unittest.TestCase):
    def test_missing_package(self):
        error = urllib.error.HTTPError(
            "url", 404, "Not Found", {}, io.BytesIO(b"")
        )
        with mock.patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(RegistryError) as context:
                CratesIndex("https://index.crates.io").versions("demo")
        self.assertIn("не найден", str(context.exception))

    def test_network_failure(self):
        error = urllib.error.URLError("offline")
        with mock.patch("urllib.request.urlopen", side_effect=error):
            with self.assertRaises(RegistryError):
                CratesIndex("https://index.crates.io").versions("demo")


if __name__ == "__main__":
    unittest.main()
