from sys import argv
from os import getcwd
from logging import basicConfig, info, INFO
from datetime import datetime
from contextlib import contextmanager

from .__init__ import *


@contextmanager
def performance_timer():
    start_time = datetime.now()
    yield
    info(f"[3/3] Completed in {str(datetime.now() - start_time)}.")


expected_args = 2  # [Entry point (provided by default), target directory]
if len(argv) != expected_args:
    if len(argv) > expected_args:
        raise TypeError(
            f"{expected_args-1} initial argument{'' if (expected_args-1) == 1 else 's'} expected, received {len(argv)-1}"
        )

    else:
        argv.append(getcwd())

basicConfig(level=INFO)

with performance_timer():
    info("[0/3] Initializing...")
    s = Scorer(argv[1])

    info("[1/3] Parsing files...")
    s.parse_all()

    info("[2/3] Plotting ranked digraph...")
    s.plot_ranked()

raise SystemExit
