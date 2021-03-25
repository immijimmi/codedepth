from abc import ABC
from typing import Iterable, Tuple


class ColourPicker(ABC):
    @classmethod
    def get(cls, file_path: str, dependency_paths: Iterable[str], dependent_paths: Iterable[str]) -> Tuple[str]:
        """
        Should return a list of 2 strings,
        the first being the colour of the node and the second the colour of the arrows
        """

        raise NotImplementedError
