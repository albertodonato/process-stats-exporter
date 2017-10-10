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
