import re
from unittest import TestCase

from lxstats.process import Process
from lxstats.testing import TestCase as LxStatsTestCase

from ..label import (
    CmdlineLabeler,
    PidLabeler,
)


class PidLabelerTests(TestCase):

    def test_labels(self):
        """PidLabeler returns the "pid" label."""
        self.assertEqual(PidLabeler().labels(), {'pid'})

    def test_call(self):
        """The labeler returns a label with the process PID."""
        process = Process(10, '/proc/10')
        self.assertEqual(PidLabeler()(process), {'pid': '10'})


class CmdlineLabelerTests(LxStatsTestCase):

    def test_labels(self):
        """The "cmd" label is returned if not match group is given."""
        labeler = CmdlineLabeler(re.compile('exec'))
        self.assertEqual(labeler.labels(), {'cmd'})

    def test_labels_with_groups(self):
        """Match labels are returned if match groups are given."""
        labeler = CmdlineLabeler(re.compile('([0-9]+)exec([a-z]+)'))
        self.assertEqual(labeler.labels(), {'match_1', 'match_2'})

    def test_labels_with_named_groups(self):
        """Named match labels are returned if match groups are given."""
        labeler = CmdlineLabeler(
            re.compile('(?P<foo>[0-9]+)exec(?P<bar>[a-z]+)'))
        self.assertEqual(labeler.labels(), {'foo', 'bar'})

    def test_call(self):
        """The labeler returns a label with the process "cmd"."""
        self.make_process_file(10, 'comm', content='exec')
        process = Process(10, self.tempdir.path / '10')
        process.collect_stats()
        labeler = CmdlineLabeler(re.compile('exec'))
        self.assertEqual(labeler(process), {'cmd': 'exec'})

    def test_call_with_groups(self):
        """The labeler returns labels with regexp matches."""
        self.make_process_file(10, 'cmdline', content='/path/to/exec')
        process = Process(10, self.tempdir.path / '10')
        process.collect_stats()
        labeler = CmdlineLabeler(re.compile('(.*)/exec'))
        self.assertEqual(labeler(process), {'match_1': '/path/to'})

    def test_call_with_named_groups(self):
        """The labeler returns labels with named regexp matches."""
        self.make_process_file(10, 'cmdline', content='/path/to/exec')
        process = Process(10, self.tempdir.path / '10')
        process.collect_stats()
        labeler = CmdlineLabeler(re.compile('(?P<prefix>.*)/exec'))
        self.assertEqual(labeler(process), {'prefix': '/path/to'})
