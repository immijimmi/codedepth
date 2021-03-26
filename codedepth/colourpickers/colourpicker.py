from abc import ABC
from typing import Tuple, Hashable


class ColourPicker(ABC):
    def __init__(self, scorer: "Scorer"):
        self._scorer = scorer

    def get(self, file_path: str) -> Tuple[str, str]:
        """
        Should return 2 strings,
        the first being the colour of the node background and the second the colour of the node border & arrows
        """

        raise NotImplementedError
