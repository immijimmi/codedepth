from abc import ABC
from typing import Generator, Dict
from re import Pattern

from .parser import Parser


class RegexParser(Parser, ABC):
    @property
    def PATTERNS(self) -> Dict[Pattern, int]:  # Abstract class constant
        raise NotImplementedError

    @classmethod
    def _get_import_nodes(cls, file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        for pattern, match_group in cls.PATTERNS.items():
            for match in pattern.findall(file_contents):
                import_node = match[match_group]

                yield import_node
