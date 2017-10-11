"""Helpers to collect processes."""

from itertools import chain

from lxstats.process import (
    Collection,
    Collector,
    CommandLineFilter)

from .label import (
    PidLabeler,
    CmdlineLabeler)


def get_process_iterator(proc='/proc', pids=None, cmdline_regexps=None):
    """Return an iterator yielding tuples with (Labeler, Process).

    Parameters:
      proc: the path to the ``/proc`` directory.
      pids: a list of PIDs of process to return. If this is specified,
            other filters are ignored.
      cmdline_regexps: a list of strings with regexps to filter process
                       command line.

    """
    if pids:
        labeler = PidLabeler()
        collection = Collection(collector=Collector(proc=proc, pids=pids))
        return ((labeler, process) for process in collection)
    elif cmdline_regexps:
        collectors = []
        for cmdline_re in cmdline_regexps:
            collection = Collection(collector=Collector(proc=proc))
            collection.add_filter(
                CommandLineFilter(cmdline_re, include_args=True))
            labeler = CmdlineLabeler(cmdline_re)
            collectors.append((labeler, process) for process in collection)
        return chain(*collectors)
    else:
        return iter(())
