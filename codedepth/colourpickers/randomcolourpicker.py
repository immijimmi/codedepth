from typing import Iterable, Tuple
from random import choice

from .colourpicker import ColourPicker


class RandomColourPicker(ColourPicker):
    colours = {}
    history = {}

    @classmethod
    def get(cls, file_path: str, dependency_paths: Iterable[str], dependent_paths: Iterable[str]) -> Tuple[str]:
        if file_path not in cls.history:
            used_colours = {colour: 0 for colour in cls.colours}
            for connection_list in (dependency_paths, dependent_paths):
                for connection_path in connection_list:
                    if connection_path in cls.history:
                        connection_colour = cls.history[connection_path]
                        used_colours[connection_colour] += 1

            min_usage = min(used_colours.values())
            min_used_colours = tuple(filter(lambda colour: used_colours[colour] == min_usage, used_colours))

            colour = choice(min_used_colours)
            cls.history[file_path] = colour

        return cls.colours[cls.history[file_path]]
