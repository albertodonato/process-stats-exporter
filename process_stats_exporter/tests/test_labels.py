from unittest import TestCase
import argparse

from ..labels import LabelAction


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
