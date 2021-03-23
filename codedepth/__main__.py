from sys import argv
from os import getcwd

from .__init__ import *

expected_args = 1
if len(argv) != expected_args+1:
    raise TypeError(
        f"{expected_args} initial argument{'' if expected_args == 1 else 's'} expected, received {len(argv)-1}"
    )

s = Scorer(argv[1])
s.generate_scores()
s.plot_ranked()
