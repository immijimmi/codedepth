from typing import Generator
from re import compile

from .parser import Parser


class LuaParser(Parser):
    filters = frozenset((
        lambda filename: filename[-9:] != r"\init.lua",
        lambda filename: filename[-14:] != r"\constants.lua",
        lambda filename: filename[-11:] != r"\config.lua"
    ))

    _node_endings = (
        r"\init.lua",
        ".lua"
    )  # TODO: Determine correct ordering to match Lua's

    _pattern = compile(r"require\((\"|\')((.|\s)*?)\1\)")

    @staticmethod
    def can_parse(filename: str) -> bool:
        return filename[-4:] == ".lua"

    @staticmethod
    def parse(file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        for match in LuaParser._pattern.findall(file_contents):
            import_node = match[1]

            target_path = LuaParser._get_import_target(working_dir, import_node)
            if target_path:
                yield target_path
