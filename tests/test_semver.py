import unittest

from src.errors import RegistryError
from src.semver import conditions, matches, parse_version, select


def bounds(requirement):
    return [(sign, item.parts) for sign, item in conditions(requirement)]


class ParseTest(unittest.TestCase):
    def test_full_version(self):
        self.assertEqual(parse_version("1.2.3").parts, (1, 2, 3))

    def test_missing_parts_are_zero(self):
        self.assertEqual(parse_version("1.2").parts, (1, 2, 0))

    def test_prerelease_is_detected(self):
        self.assertTrue(parse_version("1.0.0-beta.1").is_prerelease)

    def test_text_is_kept(self):
        self.assertEqual(parse_version("0.6.4").text, "0.6.4")

    def test_broken_version(self):
        with self.assertRaises(RegistryError):
            parse_version("not-a-version")


class RequirementTest(unittest.TestCase):
    def test_caret_on_major(self):
        self.assertEqual(
            bounds("^1.2.3"), [(">=", (1, 2, 3)), ("<", (2, 0, 0))]
        )

    def test_caret_on_minor(self):
        self.assertEqual(
            bounds("^0.2.3"), [(">=", (0, 2, 3)), ("<", (0, 3, 0))]
        )

    def test_caret_on_patch(self):
        self.assertEqual(
            bounds("^0.0.3"), [(">=", (0, 0, 3)), ("<", (0, 0, 4))]
        )

    def test_tilde(self):
        self.assertEqual(
            bounds("~1.2"), [(">=", (1, 2, 0)), ("<", (1, 3, 0))]
        )

    def test_wildcard_part(self):
        self.assertEqual(
            bounds("1.*"), [(">=", (1, 0, 0)), ("<", (2, 0, 0))]
        )

    def test_any_version(self):
        self.assertEqual(bounds("*"), [])

    def test_bare_version_is_caret(self):
        self.assertEqual(bounds("1.0"), bounds("^1.0"))

    def test_several_conditions(self):
        self.assertEqual(len(bounds(">=1.2, <1.5")), 2)


class MatchTest(unittest.TestCase):
    def test_inside_caret_range(self):
        self.assertTrue(matches(parse_version("1.4.0"), "^1.2.3"))

    def test_outside_caret_range(self):
        self.assertFalse(matches(parse_version("2.0.0"), "^1.2.3"))

    def test_exact_requirement(self):
        self.assertTrue(matches(parse_version("1.0.219"), "=1.0.219"))

    def test_exact_requirement_rejects_others(self):
        self.assertFalse(matches(parse_version("1.0.220"), "=1.0.219"))


class SelectTest(unittest.TestCase):
    def setUp(self):
        self.versions = [
            parse_version(text)
            for text in ("0.6.0", "0.6.4", "0.7.0", "0.6.5-beta")
        ]

    def test_highest_matching_version(self):
        self.assertEqual(select(self.versions, "^0.6.0").text, "0.6.4")

    def test_prerelease_is_skipped(self):
        self.assertNotIn("beta", select(self.versions, "^0.6").text)

    def test_no_matching_version(self):
        self.assertIsNone(select(self.versions, "^9.0"))


if __name__ == "__main__":
    unittest.main()
