from re import compile

from .regexparser import RegexParser


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

    _patterns = (
        compile(r"require[ \t]*\(\s*(\"|\')((.|\s)*?)\1\s*\)"),
    )

    @classmethod
    def can_parse(cls, file_path: str) -> bool:
        return file_path[-4:] == ".lua"
