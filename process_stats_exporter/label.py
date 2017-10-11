"""Metric labels."""

import re
from argparse import Action


LABEL_RE = re.compile(r'[a-z][a-z0-9_]+$')


class LabelAction(Action):
    """Action to parse and save labels from the command line."""

    def __call__(self, parser, namespace, values, option_string=None):
        labels = {}
        for value in values:
            try:
                label, value = value.split('=')
            except ValueError:
                parser.error(
                    'labels must be in the form "name=value": {}'.format(
                        value))
                return
            if not LABEL_RE.match(label):
                parser.error(
                    'invalid label: {}'.format(label))
                return
            labels[label] = value

        setattr(namespace, self.dest, labels)


class PidLabeler:
    """Return labels with process PID."""

    def __call__(self, process):
        """Return label values for the process."""
        return {'pid': str(process.pid)}

    def labels(self):
        """Return label names."""
        return ['pid']


class CmdlineLabeler:
    """Return labels based on process command line regexp.

    If groups are specified in the regexp, labels are added with groups names
    and values.
    Otherwise, a "cmd" label is added with the process name.

    """

    def __init__(self, regexp):
        self._regexp = re.compile(regexp)

    def __call__(self, process):
        """Return label values for the process."""
        return {'cmd': process.get('comm')}

    def labels(self):
        """Return label names."""
        return ['cmd']
