from abc import ABC
from typing import Iterable, Tuple, Hashable


class ColourPicker(ABC):
    def __init__(self, scorer: "Scorer"):
        self._scorer = scorer

    def get(self, key: Hashable) -> Tuple[str, str]:
        """
        Should return 2 strings,
        the first being the colour of the node background and the second the colour of the node border & arrows
        """

        raise NotImplementedError

    def set(self, key: Hashable, value: Iterable[str]) -> None:
        raise NotImplementedError
