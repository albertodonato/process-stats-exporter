"""Actions for command line parsing and validation."""

from argparse import (
    Action,
    ArgumentParser,
    Namespace,
)
import re
from typing import (
    Any,
    Optional,
)

LABEL_RE = re.compile(r'[a-z][a-z0-9_]+$')


class LabelAction(Action):
    """Action to parse and save labels from the command line."""

    def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: Any,
            option_string: Optional[str] = None):
        labels = {}
        for value in values:
            try:
                label, value = value.split('=')
            except ValueError:
                parser.error(
                    f'labels must be in the form "name=value": {value}')
                return
            if not LABEL_RE.match(label):
                parser.error(f'invalid label: {label}')
                return
            labels[label] = value

        setattr(namespace, self.dest, labels)


class CmdlineRegexpAction(Action):
    """Action to parse and validate process command line regexps."""

    def __call__(
            self,
            parser: ArgumentParser,
            namespace: Namespace,
            values: Any,
            option_string: Optional[str] = None):
        regexps = []
        for value in values:
            try:
                regexp = re.compile(value)
            except Exception as e:
                parser.error(f'compiling regexp {repr(value)}: {str(e)}')
                return

            for groupname in regexp.groupindex:
                if not LABEL_RE.match(groupname):
                    parser.error(
                        f'regexp group not valid as label: {groupname}')
                    return

            regexps.append(regexp)

        setattr(namespace, self.dest, regexps)
