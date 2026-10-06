"""Виртуальная файловая система, загружаемая из ZIP-архива в память."""
import io
import zipfile

from src.errors import VfsError

ROOT_NAME = "/"
PATH_SEP = "/"
CHARSET = "utf-8"
DEFAULT_FILES = {
    "home/user/hello.txt": "привет\nмир\n",
    "tmp/": "",
}


class VfsNode:
    """Узел дерева: каталог или файл с двоичным содержимым."""

    def __init__(self, name, is_dir, data=b""):
        self.name = name
        self.is_dir = is_dir
        self.data = data
        self.children = {}

    def names(self):
        """Отсортированные имена дочерних узлов."""
        return sorted(self.children)

    def count(self):
        """Число узлов в поддереве, включая сам узел."""
        return 1 + sum(child.count() for child in self.children.values())


class Vfs:
    """Дерево VFS целиком в памяти и путь к исходному архиву."""

    def __init__(self, root, source=None):
        self.root = root
        self.source = source

    @classmethod
    def load(cls, path):
        """Прочитать ZIP-архив в память, не распаковывая на диск."""
        return cls(_root_from_archive(_read_bytes(path)), path)

    @classmethod
    def default(cls, source=None):
        """VFS по умолчанию: /home/user/hello.txt и /tmp."""
        root = VfsNode(ROOT_NAME, True)
        for path, text in DEFAULT_FILES.items():
            _insert(root, path, text.encode(CHARSET))
        return cls(root, source)

    def save(self):
        """Записать дерево в исходный архив; False без источника."""
        if not self.source:
            return False
        try:
            with open(self.source, "wb") as stream:
                stream.write(_archive_bytes(self.root))
        except OSError as error:
            raise VfsError("не удалось сохранить VFS: " + str(error))
        return True


def _read_bytes(path):
    try:
        with open(path, "rb") as stream:
            return stream.read()
    except OSError as error:
        raise VfsError("не удалось открыть VFS: " + str(error))


def _root_from_archive(raw):
    root = VfsNode(ROOT_NAME, True)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            for info in archive.infolist():
                _insert(root, info.filename, _entry_data(archive, info))
    except zipfile.BadZipFile as error:
        raise VfsError("неверный формат VFS: " + str(error))
    return root


def _entry_data(archive, info):
    if info.is_dir():
        return b""
    try:
        return archive.read(info)
    except (zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        raise VfsError("неверный формат VFS: " + str(error))


def _insert(root, path, data):
    parts = [part for part in path.split(PATH_SEP) if part not in ("", ".")]
    if ".." in parts:
        raise VfsError("недопустимый путь в архиве: " + path)
    is_dir = path.endswith(PATH_SEP) or not parts
    node = root
    for index, part in enumerate(parts):
        last = index == len(parts) - 1
        node = _child(node, part, is_dir or not last, data)


def _child(parent, name, is_dir, data):
    existing = parent.children.get(name)
    if existing is not None:
        if existing.is_dir != is_dir:
            raise VfsError("конфликт типов узла: " + name)
        return existing
    if not parent.is_dir:
        raise VfsError("родитель не каталог: " + name)
    node = VfsNode(name, is_dir, b"" if is_dir else data)
    parent.children[name] = node
    return node


def _archive_bytes(root):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        _write_tree(archive, root, "")
    return buffer.getvalue()


def _write_tree(archive, node, prefix):
    for name in node.names():
        child = node.children[name]
        path = prefix + name
        if child.is_dir:
            archive.writestr(path + PATH_SEP, b"")
            _write_tree(archive, child, path + PATH_SEP)
        else:
            archive.writestr(path, child.data)
