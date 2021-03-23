from abc import ABC
from typing import Tuple, Callable, Generator


class Parser(ABC):
    @property
    def filters(self) -> Tuple[Callable[[], bool]]:
        raise NotImplementedError

    @staticmethod
    def can_parse(filename: str) -> bool:
        raise NotImplementedError

    @staticmethod
    def parse(file_contents: str, working_dir: str) -> Generator[str, None, None]:
        raise NotImplementedError
