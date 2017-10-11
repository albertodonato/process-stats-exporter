"""Metric labels."""

import re


class PidLabeler:
    """Return labels with process PID."""

    def __call__(self, process):
        """Return label values for the process."""
        return {'pid': str(process.pid)}

    def labels(self):
        """Return label names."""
        return {'pid'}


class CmdlineLabeler:
    """Return labels based on process command line regexp.

    If groups are specified in the regexp, labels are added with groups names
    and values.
    Otherwise, a "cmd" label is added with the process name.

    """

    _match_prefix = 'match'

    def __init__(self, regexp):
        self._regexp = re.compile(regexp)

    def __call__(self, process):
        """Return label values for the process."""
        match = self._regexp.search(process.cmd)

        groupdict = match.groupdict()
        if groupdict:
            return groupdict

        groups = match.groups()
        if groups:
            return {
                '{}_{}'.format(self._match_prefix, idx): group
                for idx, group in enumerate(groups, 1)}

        return {'cmd': process.get('comm')}

    def labels(self):
        """Return label names."""
        if self._regexp.groupindex:
            return set(self._regexp.groupindex)
        if self._regexp.groups:
            return {
                '{}_{}'.format(self._match_prefix, idx)
                for idx in range(1, self._regexp.groups + 1)}
        return {'cmd'}
