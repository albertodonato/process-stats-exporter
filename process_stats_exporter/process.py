"""Helpers to collect processes."""

from itertools import chain

from lxstats.process import (
    Collection,
    Collector,
    CommandLineFilter)


def get_process_iterator(proc='/proc', pids=None, cmdline_regexps=None):
    """Return an iterator yielding Process objects.

    Parameters:
      proc: the path to the ``/proc`` directory.
      pids: a list of PIDs of process to return. If this is specified,
            other filters are ignored.
      cmdline_regexps: a list of strings with regexps to filter process
                       command line.

    """
    if pids:
        return Collection(collector=Collector(proc=proc, pids=pids))
    elif cmdline_regexps:
        collectors = []
        for cmdline_re in cmdline_regexps:
            collection = Collection(collector=Collector(proc=proc))
            collection.add_filter(
                CommandLineFilter(cmdline_re, include_args=True))
            collectors.append(collection)
        return chain(*collectors)
    else:
        return iter(())
