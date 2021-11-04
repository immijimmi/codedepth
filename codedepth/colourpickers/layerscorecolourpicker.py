from typing import Tuple

from .colourpicker import ColourPicker
from .constants import Constants


class LayerScoreColourPicker(ColourPicker):
    COLOUR_SCALE = ("blue", "green", "yellow", "orange", "red", "purple")

    def __init__(self, scorer: "Scorer"):
        super().__init__(scorer)

        self._colours = {**Constants.COLOURS["pastel"], **Constants.COLOURS["greyscale"]}
        self._history = {}

        self._parser_filters = set()
        for parser in self._scorer.parsers:
            for func in parser.FILTERS:
                self._parser_filters.add(func)

    def get(self, file_path: str) -> Tuple[str, str]:
        if file_path not in self._history:
            if not all(func(file_path) for func in self._parser_filters):
                self._history[file_path] = "grey"

            else:
                file_layer_score = self._scorer.layer_scores[file_path]
                max_score = max(self._scorer.layer_scores.values())
                score_percentile = 0 if max_score == 0 else (file_layer_score / max_score)
                colour_index = round(score_percentile * (len(self.COLOUR_SCALE) - 1))

                self._history[file_path] = self.COLOUR_SCALE[colour_index]

        return self._colours[self._history[file_path]]
