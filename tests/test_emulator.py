import io
import os
import unittest

from src.errors import ExitRequest
from src.parser import parse
from src.shell import Shell


def shell_with_output():
    stream = io.StringIO()
    return Shell(output=stream), stream


class ParseTest(unittest.TestCase):
    def test_empty_line(self):
        self.assertEqual(parse("   "), (None, []))

    def test_command_and_arguments(self):
        self.assertEqual(parse("ls -l /etc"), ("ls", ["-l", "/etc"]))

    def test_variable_expansion(self):
        os.environ["VFS_DEMO"] = "demo"
        self.assertEqual(parse("ls $VFS_DEMO"), ("ls", ["demo"]))

    def test_unknown_variable(self):
        os.environ.pop("VFS_MISSING", None)
        self.assertEqual(parse("ls $VFS_MISSING"), ("ls", [""]))

    def test_lonely_dollar_is_kept(self):
        self.assertEqual(parse("ls 5$"), ("ls", ["5$"]))


class ShellTest(unittest.TestCase):
    def setUp(self):
        self.shell, self.stream = shell_with_output()

    def run_line(self, line):
        self.shell.run_line(line)
        return self.stream.getvalue()

    def test_prompt_contains_vfs_name(self):
        self.assertIn(":vfs$ ", self.shell.prompt())

    def test_prompt_contains_user_and_host(self):
        self.assertIn("@", self.shell.prompt())

    def test_ls_stub(self):
        self.assertEqual(self.run_line("ls -a /tmp"), "ls -a /tmp\n")

    def test_cd_stub(self):
        self.assertEqual(self.run_line("cd /tmp"), "cd /tmp\n")

    def test_unknown_command(self):
        self.assertIn("команда не найдена", self.run_line("wat"))

    def test_bad_arguments(self):
        self.assertIn("слишком много аргументов", self.run_line("cd a b"))

    def test_bad_exit_code(self):
        self.assertIn("числовой аргумент", self.run_line("exit now"))

    def test_exit_requests_stop(self):
        with self.assertRaises(ExitRequest) as context:
            self.shell.execute("exit 3")
        self.assertEqual(context.exception.code, 3)


if __name__ == "__main__":
    unittest.main()
