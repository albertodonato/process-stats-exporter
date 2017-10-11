from lxstats.testing import TestCase

from ..process import get_process_iterator
from ..label import (
    PidLabeler,
    CmdlineLabeler)


class GetProcessIteratorTests(TestCase):

    def test_process_iterator_pids(self):
        """An iterator yielding processes with specified PIDs is returned."""
        self.make_process_file(10, 'cmdline')
        self.make_process_file(20, 'cmdline')
        self.make_process_file(30, 'cmdline')
        self.make_process_file(40, 'cmdline')
        iterator = get_process_iterator(proc=self.tempdir.path, pids=[10, 30])
        labelers, processes = zip(*iterator)
        for labeler in labelers:
            self.assertIsInstance(labeler, PidLabeler)
        self.assertCountEqual([process.pid for process in processes], [10, 30])

    def test_process_iterator_cmdline_regexps(self):
        """An iterator yielding processes with matching cmdline is returned."""
        self.make_process_file(10, 'cmdline', content='foo\x00bar\x00')
        self.make_process_file(20, 'cmdline', content='another\x00command\x00')
        self.make_process_file(30, 'cmdline', content='baz\x00bza\x00')
        self.make_process_file(40, 'cmdline', content='something\x00else\x00')
        iterator = get_process_iterator(
            proc=self.tempdir.path, cmdline_regexps=['foo', 'baz'])
        labelers, processes = zip(*iterator)
        for labeler in labelers:
            self.assertIsInstance(labeler, CmdlineLabeler)
        self.assertCountEqual([process.pid for process in processes], [10, 30])

    def test_process_iterator_cmdline_regexps_matches_args(self):
        """Cmdline regexps match the full cmdline"""
        self.make_process_file(10, 'cmdline', content='foo\x00bar\x00')
        self.make_process_file(20, 'cmdline', content='another\x00command\x00')
        iterator = get_process_iterator(
            proc=self.tempdir.path, cmdline_regexps=['bar'])
        _, processes = zip(*iterator)
        self.assertCountEqual([process.pid for process in processes], [10])

    def test_process_iterator_empty(self):
        """If no args are specified, an empty iterator is returned."""
        self.assertEqual([], list(get_process_iterator()))
