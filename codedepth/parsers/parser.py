from abc import ABC
from os import path as ospath
from typing import Tuple, Callable, Generator, FrozenSet, Optional


class Parser(ABC):
    @property
    def filters(self) -> FrozenSet[Callable[[], bool]]:
        raise NotImplementedError

    @property
    def _node_endings(self) -> Tuple[str]:
        raise NotImplementedError

    @staticmethod
    def can_parse(filename: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def parse(file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        raise NotImplementedError

    @classmethod
    def _get_import_target(cls, import_node_starting_dir: str, import_node: str) -> Optional[str]:
        working_target = import_node_starting_dir + "\\" + import_node.replace(".", "\\")

        for path_ending in cls._node_endings:
            result = working_target + path_ending
            if ospath.isfile(result):
                return result
