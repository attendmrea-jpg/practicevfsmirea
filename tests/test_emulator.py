import io
import os
import tempfile
import unittest
import zipfile

from src.errors import ExitRequest, ScriptError, VfsError
from src.main import _parse_args
from src.parser import parse
from src.shell import Shell
from src.vfs import Vfs
from tests.tools import make_vfs


def shell_with_output():
    stream = io.StringIO()
    return Shell(output=stream), stream


def script_file(text):
    handle, path = tempfile.mkstemp(suffix=".vsh")
    with os.fdopen(handle, "w", encoding="utf-8") as stream:
        stream.write(text)
    return path


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


class ConfigTest(unittest.TestCase):
    def test_defaults_are_empty(self):
        args = _parse_args([])
        self.assertIsNone(args.vfs_path)
        self.assertIsNone(args.script_path)

    def test_parses_both_parameters(self):
        args = _parse_args(["--vfs", "a.zip", "--script", "b.vsh"])
        self.assertEqual(args.vfs_path, "a.zip")
        self.assertEqual(args.script_path, "b.vsh")

    def test_debug_output_lists_parameters(self):
        shell, stream = shell_with_output()
        shell.vfs_path = "a.zip"
        shell.script_path = "b.vsh"
        shell.write_debug()
        self.assertIn("a.zip", stream.getvalue())
        self.assertIn("b.vsh", stream.getvalue())

    def test_debug_output_marks_missing_parameters(self):
        shell, stream = shell_with_output()
        shell.write_debug()
        self.assertIn("<не задан>", stream.getvalue())

    def test_vfs_name_comes_from_path(self):
        shell = Shell(vfs_path="/some/dir/demo.zip")
        self.assertIn(":demo$ ", shell.prompt())


class ScriptTest(unittest.TestCase):
    def setUp(self):
        self.shell, self.stream = shell_with_output()

    def test_echoes_input_and_output(self):
        path = script_file("ls one\n")
        self.shell.run_script(path)
        os.unlink(path)
        self.assertIn(self.shell.prompt() + "ls one", self.stream.getvalue())
        self.assertIn("\nls one\n", self.stream.getvalue())

    def test_stops_at_first_error(self):
        path = script_file("ls one\nbad\nls three\n")
        with self.assertRaises(ScriptError):
            self.shell.run_script(path)
        os.unlink(path)
        self.assertNotIn("ls three", self.stream.getvalue())

    def test_missing_file_is_reported(self):
        with self.assertRaises(ScriptError):
            self.shell.run_script("nosuch.vsh")


class VfsTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        make_vfs.build(self.dir.name)

    def path(self, name):
        return os.path.join(self.dir.name, name + ".zip")

    def test_minimal_vfs(self):
        self.assertEqual(Vfs.load(self.path("vfs_min")).root.names(), [])

    def test_several_files(self):
        root = Vfs.load(self.path("vfs_files")).root
        self.assertEqual(
            root.names(), ["logo.bin", "notes.txt", "readme.txt"]
        )

    def test_three_levels(self):
        root = Vfs.load(self.path("vfs_deep")).root
        docs = root.children["home"].children["user"].children["docs"]
        self.assertIn("report.txt", docs.names())

    def test_binary_content(self):
        root = Vfs.load(self.path("vfs_files")).root
        self.assertEqual(root.children["logo.bin"].data, bytes(range(16)))

    def test_load_does_not_modify_archive(self):
        path = self.path("vfs_deep")
        with open(path, "rb") as stream:
            before = stream.read()
        Vfs.load(path)
        with open(path, "rb") as stream:
            self.assertEqual(stream.read(), before)

    def test_missing_archive(self):
        with self.assertRaises(VfsError):
            Vfs.load(self.path("nosuch"))

    def test_broken_archive(self):
        path = script_file("не zip")
        with self.assertRaises(VfsError):
            Vfs.load(path)
        os.unlink(path)

    def test_path_traversal_is_rejected(self):
        path = self.path("evil")
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("../evil.txt", b"x")
        with self.assertRaises(VfsError):
            Vfs.load(path)

    def test_load_reports_node_count(self):
        shell, stream = shell_with_output()
        shell.vfs_path = self.path("vfs_deep")
        shell.load_vfs()
        self.assertIn("vfs узлов = 10", stream.getvalue())


class VfsInitTest(unittest.TestCase):
    def test_replaces_tree(self):
        shell, _ = shell_with_output()
        shell.vfs.root.children.clear()
        shell.run_line("vfs-init")
        self.assertEqual(shell.vfs.root.names(), ["home", "tmp"])

    def test_rejects_arguments(self):
        shell, stream = shell_with_output()
        shell.run_line("vfs-init a")
        self.assertIn("не поддерживаются", stream.getvalue())

    def test_rewrites_physical_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            make_vfs.build(directory)
            path = os.path.join(directory, "vfs_deep.zip")
            shell = Shell(vfs_path=path, output=io.StringIO())
            shell.load_vfs()
            shell.run_line("vfs-init")
            self.assertEqual(Vfs.load(path).root.names(), ["home", "tmp"])


if __name__ == "__main__":
    unittest.main()
