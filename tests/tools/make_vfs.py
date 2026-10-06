"""Генератор тестовых ZIP-образов VFS (архивы в репозитории не хранятся).

Использование: python3 make_vfs.py КАТАЛОГ
Создаёт vfs_min.zip, vfs_files.zip и vfs_deep.zip.
"""
import os
import sys
import zipfile

BINARY = bytes(range(16))
IMAGES = {
    "vfs_min": [("", b"")],
    "vfs_files": [
        ("readme.txt", "эмулятор оболочки\nвариант 19\n".encode("utf-8")),
        ("notes.txt", "первая строка\nвторая строка\n".encode("utf-8")),
        ("logo.bin", BINARY),
    ],
    "vfs_deep": [
        ("home/", b""),
        ("home/user/", b""),
        ("home/user/docs/", b""),
        ("home/user/docs/report.txt", "отчёт\n".encode("utf-8")),
        ("home/user/docs/data.bin", BINARY),
        ("home/user/hello.txt", "привет\n".encode("utf-8")),
        ("etc/", b""),
        ("etc/motd", "добро пожаловать\n".encode("utf-8")),
        ("tmp/", b""),
    ],
}


def build(directory):
    """Создать все образы в каталоге и вернуть их пути."""
    paths = []
    for name, entries in IMAGES.items():
        path = os.path.join(directory, name + ".zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
            for entry, data in entries:
                if entry:
                    archive.writestr(entry, data)
        paths.append(path)
    return paths


if __name__ == "__main__":
    build(sys.argv[1])
