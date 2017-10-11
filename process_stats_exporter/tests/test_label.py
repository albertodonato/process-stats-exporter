import os
import argparse
from unittest import TestCase

from lxstats.process import Process
from lxstats.testing import TestCase as LxStatsTestCase

from ..label import (
    LabelAction,
    PidLabeler,
    CmdlineLabeler)


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


class PidLabelerTests(TestCase):

    def test_labels(self):
        """PidLabeler returns the "pid label."""
        self.assertEqual(PidLabeler().labels(), ['pid'])

    def test_call(self):
        """The labeler returns a label with the process PID."""
        process = Process(10, '/proc/10')
        self.assertEqual(PidLabeler()(process), {'pid': '10'})


class CmdlineLabelerTests(LxStatsTestCase):

    def test_labels(self):
        """CmdlineLabelerTests returns the "cmd" label."""
        self.assertEqual(CmdlineLabeler('exec').labels(), ['cmd'])

    def test_call(self):
        """The labeler returns a label with the process "cmd"."""
        self.make_process_file(10, 'comm', content='exec')
        process = Process(10, os.path.join(self.tempdir.path, '10'))
        process.collect_stats()
        self.assertEqual(CmdlineLabeler('exec')(process), {'cmd': 'exec'})
