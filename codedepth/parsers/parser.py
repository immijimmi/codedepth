from abc import ABC
from os import path as ospath
from typing import Tuple, Callable, Generator, FrozenSet, Optional

from ..constants import Constants


class Parser(ABC):
    @property
    def filters(self) -> FrozenSet[Callable[[str], bool]]:
        raise NotImplementedError

    @property
    def _node_endings(self) -> Tuple[str]:
        raise NotImplementedError

    @classmethod
    def can_parse(cls, file_path: str) -> bool:
        """
        Indicates whether the file is supported by the parser class this is called on.
        For any files that should never be considered local dependencies, this should return False
        (for example, files inside a node_modules folder for JS projects)
        """

        raise NotImplementedError

    @classmethod
    def parse(cls, file_contents: str, file_dir: str, working_dir: str) -> Generator[str, None, None]:
        raise NotImplementedError

    @classmethod
    def _get_import_target(cls, import_node_starting_dir: str, import_node: str) -> Optional[str]:
        working_target = import_node_starting_dir + Constants.path_delimiter
        working_target += import_node.replace(".", Constants.path_delimiter).replace(Constants.non_path_delimiter, Constants.path_delimiter)

        for path_ending in cls._node_endings:
            result = working_target + path_ending
            if ospath.isfile(result):
                return result
