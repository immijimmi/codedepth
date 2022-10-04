from abc import ABC
from os import path as ospath, sep
from typing import Tuple, Callable, Generator, FrozenSet, Optional

from .methods import Decorators


class Parser(ABC):
    @Decorators.classproperty
    def FILTERS(cls) -> FrozenSet[Callable[[str], bool]]:
        raise NotImplementedError

    @Decorators.classproperty
    def NODE_ENDINGS(cls) -> Tuple[str, ...]:
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
        working_target = import_node_starting_dir + sep
        working_target += import_node.replace(
            ".", sep
        ).replace(
            non_sep := {"\\": "/", "/": "\\"}[sep], sep
        )

        for path_ending in cls.NODE_ENDINGS:
            result = working_target + path_ending
            if ospath.isfile(result):
                return result
