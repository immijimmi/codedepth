from abc import ABC
from typing import Iterable, Tuple


class ColourPicker(ABC):
    @classmethod
    def get(cls, file_path: str, dependency_paths: Iterable[str], dependent_paths: Iterable[str]) -> Tuple[str, str]:
        """
        Should return 2 strings,
        the first being the colour of the node background and the second the colour of the node border & arrows
        """

        raise NotImplementedError
