from ast import walk, parse, Import, ImportFrom
from os import path as ospath
from typing import Generator

from .parser import Parser


class PyParser(Parser):
    filters = frozenset((
        lambda file_path: file_path[-12:] != r"\__init__.py",
        lambda file_path: file_path[-13:] != r"\constants.py",
        lambda file_path: file_path[-10:] != r"\config.py",
        lambda file_path: file_path[-12:] != r"\__main__.py"
    ))

    _node_endings = (
        r"\__init__.py",
        r"\__init__.pyw",
        ".py",
        ".pyw"
    )

    @staticmethod
    def can_parse(file_path: str) -> bool:
        return file_path[-3:] == ".py" or file_path[-4:] == ".pyw"

    @staticmethod
    def parse(file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        nodes = walk(parse(file_contents))

        for node in nodes:
            if isinstance(node, Import):
                for name_node in node.names:
                    target_path = PyParser._get_import_target(file_dir, name_node.name)
                    if target_path:
                        yield target_path

            elif isinstance(node, ImportFrom):
                offset_file_dir = file_dir

                if node.level > 1:
                    for i in range(node.level-1):
                        offset_file_dir = ospath.dirname(offset_file_dir)  # Go up 1 directory
                if node.module:
                    target_path = PyParser._get_import_target(offset_file_dir, node.module)
                    if target_path:
                        yield target_path

                else:
                    for name_node in node.names:
                        target_path = PyParser._get_import_target(offset_file_dir, name_node.name)
                        if target_path:
                            yield target_path
