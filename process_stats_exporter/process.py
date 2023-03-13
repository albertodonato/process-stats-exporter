"""Helpers to collect processes."""

from collections.abc import Iterable
from itertools import chain

from lxstats.process import (
    Collection,
    Collector,
    CommandLineFilter,
    Process,
)

from .label import (
    CmdlineLabeler,
    Labeler,
    PidLabeler,
)

ProcessIteratorResult = Iterable[tuple[Labeler, Process]]


def get_process_iterator(
    proc: str = "/proc",
    pids: list[str] | None = None,
    cmdline_regexps: list[str] | None = None,
) -> ProcessIteratorResult:
    """Return an iterator yielding tuples with (Labeler, Process).

    :param proc: the path to the ``/proc`` directory.
    :param pids: a list of PIDs of process to return. If this is
        specified, other filters are ignored.
    :param cmdline_regexps: a list of strings with regexps to filter
        process command line.

    """
    labeler: Labeler
    if pids:
        labeler = PidLabeler()
        collection = Collection(collector=Collector(proc=proc, pids=pids))
        return ((labeler, process) for process in collection)
    elif cmdline_regexps:
        collectors = []
        for cmdline_re in cmdline_regexps:
            collection = Collection(collector=Collector(proc=proc))
            collection.add_filter(
                CommandLineFilter(cmdline_re, include_args=True)
            )
            labeler = CmdlineLabeler(cmdline_re)
            collectors.append((labeler, process) for process in collection)
        return chain(*collectors)
    else:
        return iter(())
