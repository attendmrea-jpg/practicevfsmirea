import os
import tempfile
import unittest

from src.errors import RegistryError
from src.package import Package
from src.registry import Dependency
from src.sources import RegistrySource, TestSource, load_test_repository

RECORDS = {
    "libc": [
        {"vers": "0.2.160", "deps": []},
        {"vers": "0.2.170", "deps": []},
        {"vers": "0.3.0", "deps": [], "yanked": True},
    ],
}


class FakeIndex:
    def __init__(self):
        self.requested = []

    def versions(self, name):
        self.requested.append(name)
        return RECORDS[name]

    def direct_dependencies(self, name, version):
        return [Dependency("libc", "^0.2")]


def repository_file(text):
    handle, path = tempfile.mkstemp(suffix=".graph")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(text)
    return path


class TestRepositoryTest(unittest.TestCase):
    def load(self, text):
        path = repository_file(text)
        self.addCleanup(os.unlink, path)
        return load_test_repository(path)

    def test_dependencies_are_read(self):
        self.assertEqual(self.load("A -> B, C\n")["A"], ["B", "C"])

    def test_spaces_instead_of_commas(self):
        self.assertEqual(self.load("A -> B C\n")["A"], ["B", "C"])

    def test_package_without_dependencies(self):
        self.assertEqual(self.load("A ->\n")["A"], [])

    def test_comments_are_skipped(self):
        self.assertEqual(list(self.load("# note\nA -> B\n")), ["A"])

    def test_arrow_is_required(self):
        with self.assertRaises(RegistryError):
            self.load("A B\n")

    def test_names_must_be_uppercase(self):
        with self.assertRaises(RegistryError):
            self.load("a -> B\n")

    def test_empty_repository(self):
        with self.assertRaises(RegistryError):
            self.load("# only a comment\n")

    def test_missing_file(self):
        with self.assertRaises(RegistryError):
            load_test_repository("nosuchfile.graph")


class TestSourceTest(unittest.TestCase):
    def setUp(self):
        self.source = TestSource({"A": ["B"], "B": []})

    def test_direct_dependencies(self):
        self.assertEqual(self.source.direct(Package("A")), [Package("B")])

    def test_unknown_package_is_a_leaf(self):
        self.assertEqual(self.source.direct(Package("Z")), [])

    def test_contains(self):
        self.assertTrue(self.source.contains("A"))
        self.assertFalse(self.source.contains("Z"))


class RegistrySourceTest(unittest.TestCase):
    def setUp(self):
        self.index = FakeIndex()
        self.source = RegistrySource(self.index)

    def test_requirement_is_resolved_to_version(self):
        found = self.source.direct(Package("demo", "1.0.0"))
        self.assertEqual(found, [Package("libc", "0.2.170")])

    def test_yanked_version_is_skipped(self):
        found = self.source.direct(Package("demo", "1.0.0"))
        self.assertNotEqual(found[0].version, "0.3.0")

    def test_resolution_is_cached(self):
        self.source.direct(Package("demo", "1.0.0"))
        self.source.direct(Package("demo", "1.0.0"))
        self.assertEqual(self.index.requested, ["libc"])

    def test_unsatisfiable_requirement(self):
        self.index.direct_dependencies = lambda name, version: [
            Dependency("libc", "^9.0")
        ]
        with self.assertRaises(RegistryError):
            self.source.direct(Package("demo", "1.0.0"))


if __name__ == "__main__":
    unittest.main()
