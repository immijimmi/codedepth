from typing import Tuple, Hashable
from random import choice

from .colourpicker import ColourPicker
from .constants import Constants


class RandomColourPicker(ColourPicker):
    def __init__(self, scorer: "Scorer"):
        super().__init__(scorer)

        self._colours = Constants.colours["pastel"]
        self._history = {}

    def get(self, file_path: str) -> Tuple[str, str]:
        if file_path not in self._history:
            used_colours = {colour: 0 for colour in self._colours}

            for connection_list in (self._scorer.imports[file_path], self._scorer.exports[file_path]):
                for connection_path in connection_list:
                    if connection_path in self._history:
                        connection_colour = self._history[connection_path]
                        used_colours[connection_colour] += 1

            min_usage = min(used_colours.values())
            min_used_colours = tuple(filter(lambda colour: used_colours[colour] == min_usage, used_colours))

            colour = choice(min_used_colours)
            self._history[file_path] = colour

        return self._colours[self._history[file_path]]
