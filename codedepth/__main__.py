from sys import argv
from os import getcwd

from .__init__ import *

expected_args = 2  # [Entry point (provided by default), target directory]
if len(argv) != expected_args:
    if len(argv) > expected_args:
        raise TypeError(
            f"{expected_args-1} initial argument{'' if (expected_args-1) == 1 else 's'} expected, received {len(argv)-1}"
        )

    else:
        argv.append(getcwd())

s = Scorer(argv[1])
s.parse_all()
s.plot_ranked()
