from sys import argv
from os import getcwd
from logging import basicConfig, info, INFO

from .__init__ import *

expected_args = 2  # [Entry point (provided by default), target directory]
if len(argv) != expected_args:
    if len(argv) > expected_args:
        raise TypeError(
            f"{expected_args-1} initial argument{'' if (expected_args-1) == 1 else 's'} expected, received {len(argv)-1}"
        )

    else:
        argv.append(getcwd())

basicConfig(level=INFO)

info("Initializing...")
s = Scorer(argv[1])

info("Parsing files...")
s.parse_all()

info("Plotting ranked digraph...")
s.plot_ranked()
