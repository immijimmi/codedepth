from abc import ABC
from os import path as ospath
from typing import Tuple, Callable, Generator, FrozenSet, Optional

from ..constants import Constants as ScorerConstants


class Parser(ABC):
    @property
    def FILTERS(self) -> FrozenSet[Callable[[str], bool]]:  # Abstract class constant
        raise NotImplementedError

    @property
    def NODE_ENDINGS(self) -> Tuple[str, ...]:  # Abstract class constant
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
        working_target = import_node_starting_dir + ScorerConstants.PATH_DELIMITER
        working_target += import_node.replace(
            ".", ScorerConstants.PATH_DELIMITER
        ).replace(
            ScorerConstants.NON_PATH_DELIMITER, ScorerConstants.PATH_DELIMITER
        )

        for path_ending in cls.NODE_ENDINGS:
            result = working_target + path_ending
            if ospath.isfile(result):
                return result
