from .colourpickers import LayerScoreColourPicker


class Config:
    USE_DEFAULT_FILTERS = False

    COLOUR_PICKER_CLS = LayerScoreColourPicker

    RANKED_STYLES = {
        "node": {
            "fontname": "helvetica",
        },
        "edge": {

        },
    }
