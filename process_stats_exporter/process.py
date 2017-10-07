"""Helpers to collect processes."""

from itertools import chain

from lxstats.process import (
    Collection,
    Collector,
    CommandLineFilter)


def get_process_iterator(proc='/proc', pids=None, name_regexps=None):
    """Return an iterator yielding Process objects.

    Parameters:
      proc: the path to the ``/proc`` directory.
      pids: a list of PIDs of process to return. If this is specified,
            other filters are ignored.
      name_regexps: a list of strings with regexps to filter process names.

    """
    if pids:
        return Collection(collector=Collector(proc=proc, pids=pids))
    elif name_regexps:
        collectors = []
        for name_re in name_regexps:
            collection = Collection(collector=Collector(proc=proc))
            collection.add_filter(CommandLineFilter(name_re))
            collectors.append(collection)
        return chain(*collectors)
    else:
        return iter(())
