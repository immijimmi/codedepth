from typing import Tuple

from .colourpicker import ColourPicker
from .constants import Constants


class LayerScoreColourPicker(ColourPicker):
    _colour_scale = ("blue", "green", "yellow", "orange", "red", "purple")

    def __init__(self, scorer: "Scorer"):
        super().__init__(scorer)

        self._colours = {**Constants.colours["pastel"], **Constants.colours["greyscale"]}
        self._history = {}

        self._parser_filters = set()
        for parser in self._scorer.import_parsers:
            for func in parser.filters:
                self._parser_filters.add(func)

    def get(self, file_path: str) -> Tuple[str, str]:
        if file_path not in self._history:
            if not all(func(file_path) for func in self._parser_filters):
                self._history[file_path] = "grey"

            else:
                file_layer_score = self._scorer.layer_scores[file_path]
                score_percentile = file_layer_score / max(self._scorer.layer_scores.values())
                colour_index = round(score_percentile * (len(self._colour_scale)-1))

                self._history[file_path] = self._colour_scale[colour_index]

        return self._colours[self._history[file_path]]
