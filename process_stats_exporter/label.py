"""Labelers to return metric labels for processes."""

import abc
from typing import (
    Mapping,
    Set,
)

from lxstats.process import Process


class Labeler(abc.ABC):
    """Labeler base class."""

    @abc.abstractmethod
    def __call__(self, process: Process) -> Mapping[str, str]:
        """Return a mapping of label names to values.

        Subclasses must implement this method.

        """

    @abc.abstractmethod
    def labels(self) -> Set[str]:
        """Return a set of label names.

        Subclasses must implement this method.

        """


class PidLabeler(Labeler):
    """Return labels with process PID."""

    def __call__(self, process: Process) -> Mapping[str, str]:
        """Return label values for the process."""
        return {"pid": str(process.pid)}

    def labels(self) -> Set[str]:
        """Return label names."""
        return {"pid"}


class CmdlineLabeler(Labeler):
    """Return labels based on process command line regexp.

    If groups are specified in the regexp, labels are added with groups names
    and values.
    Otherwise, a "cmd" label is added with the process name.

    """

    _match_prefix = "match"

    def __init__(self, regexp):
        self._regexp = regexp

    def __call__(self, process: Process) -> Mapping[str, str]:
        """Return label values for the process."""
        match = self._regexp.search(process.cmd)

        groupdict = match.groupdict()
        if groupdict:
            return dict(groupdict)

        groups = match.groups()
        if groups:
            return {
                f"{self._match_prefix}_{idx}": group
                for idx, group in enumerate(groups, 1)
            }

        return {"cmd": process.get("comm")}

    def labels(self) -> Set[str]:
        """Return label names."""
        if self._regexp.groupindex:
            return set(self._regexp.groupindex)
        if self._regexp.groups:
            return {
                f"{self._match_prefix}_{idx}"
                for idx in range(1, self._regexp.groups + 1)
            }
        return {"cmd"}
