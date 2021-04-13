from re import compile
from typing import Generator

from .regexparser import RegexParser
from .constants import Patterns


class LuaParser(RegexParser):
    filters = frozenset((
        lambda file_path: file_path[-9:] != r"\init.lua",
        lambda file_path: file_path[-14:] != r"\constants.lua",
        lambda file_path: file_path[-11:] != r"\config.lua"
    ))

    _node_endings = (
        r"\init.lua",
        ".lua"
    )  # TODO: Determine correct ordering to match Lua's

    _patterns = {
        **Patterns.require
    }

    @classmethod
    def can_parse(cls, file_path: str) -> bool:
        return file_path[-4:] == ".lua"

    @classmethod
    def parse(cls, file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        for import_node in cls._get_import_nodes(file_contents, file_dir, working_dir):
            target_path = cls._get_import_target(working_dir, import_node)

            if target_path:
                yield target_path
