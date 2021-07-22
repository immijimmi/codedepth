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

            while True:
                latest_char = None
                for char_index, char in enumerate(import_node):
                    if char != ".":
                        latest_char = char
                        break
                    elif char_index == 0:
                        pass
                    else:
                        offset_file_dir = ospath.dirname(offset_file_dir)  # Go up 1 directory

                if latest_char != Constants.path_delimiter:
                    break

            import_node = import_node.lstrip(".")
            import_node = import_node.lstrip("/").lstrip("\\")
            target_path = cls._get_import_target(offset_file_dir, import_node)

            if target_path:
                yield target_path
