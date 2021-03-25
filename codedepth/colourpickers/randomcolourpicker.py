from typing import Iterable, Tuple, Hashable
from random import choice

from .colourpicker import ColourPicker
from .constants import Constants


class RandomColourPicker(ColourPicker):
    def __init__(self, scorer: "Scorer"):
        super().__init__(scorer)

        self._colours = Constants.colours["pastel"]
        self._history = {}

    def get(self, key: Hashable) -> Tuple[str, str]:
        if key not in self._history:  # Key will be assumed to be a file path if a colour is not generated for it yet
            used_colours = {colour: 0 for colour in self._colours}

            for connection_list in (self._scorer.imports[key], self._scorer.exports[key]):
                for connection_path in connection_list:
                    if connection_path in self._history:
                        connection_colour = self._history[connection_path]
                        used_colours[connection_colour] += 1

            min_usage = min(used_colours.values())
            min_used_colours = tuple(filter(lambda colour: used_colours[colour] == min_usage, used_colours))

            colour = choice(min_used_colours)
            self._history[key] = colour

        return self._colours[self._history[key]]

    def set(self, key: Hashable, value: Iterable[str]) -> None:
        self._history[key] = tuple(value)
