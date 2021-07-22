from typing import Generator
from re import compile
from os import path as ospath

from .regexparser import RegexParser
from .constants import Patterns, Constants as ParserConstants
from ..constants import Constants


class JsParser(RegexParser):
    filters = frozenset((
        # TODO
    ))

    _node_endings = (
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ""
    )  # TODO: Possibly missing entries, and need to determine correct ordering to match JS's

    _patterns = {
        **Patterns.require,
        compile(r"import [\w\{\}\s]*? from (\"|\')((.|\s)*?)\1"): 1,  # `import _ from 'module'`
        compile(r"import (\"|\')((.|\s)*?)\1"): 1,  # `import 'module'`
    }  # TODO: Add all styles of import

    @classmethod
    def can_parse(cls, file_path: str) -> bool:
        result = file_path[-3:] in (".js", ".ts") or file_path[-4:] in (".jsx", ".tsx")
        result = result and (ParserConstants.node_modules_fragment not in file_path)
        return result

    @classmethod
    def parse(cls, file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        for import_node in cls._get_import_nodes(file_contents, file_dir, working_dir):
            offset_file_dir = file_dir

            directory_offset_total = 0
            relative_chars = ""
            previous_char = None
            for char in import_node:
                if char == ".":
                    if previous_char == ".":
                        directory_offset_total += 1

                    relative_chars += char
                elif char in (Constants.path_delimiter, Constants.non_path_delimiter):
                    relative_chars += char
                else:
                    break

                previous_char = char

            for i in range(directory_offset_total):
                offset_file_dir = ospath.dirname(offset_file_dir)  # Go up 1 directory

            import_node = import_node.lstrip(relative_chars)  # Remove relative characters from front of import node

            target_path = cls._get_import_target(offset_file_dir, import_node)

            if target_path:
                yield target_path
