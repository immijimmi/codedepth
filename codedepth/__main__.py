from sys import argv
from os import getcwd
from logging import basicConfig, info, INFO
from datetime import datetime
from contextlib import contextmanager

from .__init__ import Scorer


@contextmanager
def performance_timer(on_finish: Callable[[datetime, datetime], None]):
    start_time = datetime.now()
    yield
    end_time = datetime.now()
    on_finish(start_time, end_time)


expected_args = 2  # [Entry point (provided by default), target directory]
if len(argv) != expected_args:
    if len(argv) > expected_args:
        raise TypeError(
            f"{expected_args-1} initial argument{'' if (expected_args-1) == 1 else 's'} expected, received {len(argv)-1}"
        )

    else:
        argv.append(getcwd())

basicConfig(level=INFO)

with performance_timer(lambda start, end: info(f"[3/3] Completed in {end - start}.")):
    info("[0/3] Initializing...")
    scorer = Scorer(argv[1])

    info("[1/3] Parsing files...")
    scorer.parse_all()

    info("[2/3] Plotting ranked digraph...")
    scorer.plot_ranked()
