import argparse
from unittest import TestCase

from ..cmdline import (
    CmdlineRegexpAction,
    LabelAction,
)


class LabelActionTests(TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-l', nargs='+', action=LabelAction)
        self.error_messages = []
        self.parser.error = self.error_messages.append

    def test_parse_labels(self):
        """LabelAction parses labels into a dict mapping names to values."""
        args = self.parser.parse_args(['-l', 'foo=bar', 'baz=bza'])
        self.assertEqual(args.l, {'foo': 'bar', 'baz': 'bza'})
        self.assertEqual(self.error_messages, [])

    def test_invalid_format(self):
        """If labels are not specified as name=value, an error is raised."""
        self.parser.parse_args(['-l', 'foobar'])
        self.assertEqual(
            self.error_messages,
            ['labels must be in the form "name=value": foobar'])

    def test_invalid_name(self):
        """Invalid label names raise an error."""
        self.parser.parse_args(['-l', 'i am invalid=bar'])
        self.assertEqual(self.error_messages, ['invalid label: i am invalid'])


class CmdlineRegexpActionTests(TestCase):

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-R', nargs='+', action=CmdlineRegexpAction)
        self.error_messages = []
        self.parser.error = self.error_messages.append

    def test_parse_regexps(self):
        """CmdlineRegexpAction parses and compiles strings into regexps."""
        args = self.parser.parse_args(['-R', '.*bash', 'ls.*'])
        self.assertEqual(
            [regex.pattern for regex in args.R], ['.*bash', 'ls.*'])
        self.assertEqual(self.error_messages, [])

    def test_invalid_regexp(self):
        """If a regexp is malformed, an error is raised."""
        self.parser.parse_args(['-R', '(?P<wrong.*)'])
        self.assertEqual(
            self.error_messages, [
                "compiling regexp '(?P<wrong.*)': missing >, unterminated "
                "name at position 4"
            ])

    def test_invalid_regexp_group_name(self):
        """If a regexp group name is invalid as label, an error is raised."""
        self.parser.parse_args(['-R', '(?P<_invalid>.*)'])
        self.assertEqual(
            self.error_messages, ['regexp group not valid as label: _invalid'])
