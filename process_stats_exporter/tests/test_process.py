from lxstats.testing import TestCase

from ..process import get_process_iterator


class GetProcessIteratorTests(TestCase):

    def test_process_iterator_pids(self):
        """An iterator yielding processes with specified PIDs is returned."""
        self.make_process_file(10, 'cmdline')
        self.make_process_file(20, 'cmdline')
        self.make_process_file(30, 'cmdline')
        self.make_process_file(40, 'cmdline')
        iterator = get_process_iterator(proc=self.tempdir.path, pids=[10, 30])
        self.assertCountEqual([process.pid for process in iterator], [10, 30])

    def test_process_iterator_name_regexps(self):
        """An iterator yielding processes with matching names is returned."""
        self.make_process_file(10, 'cmdline', content='foo\x00bar\x00')
        self.make_process_file(20, 'cmdline', content='another\x00command\x00')
        self.make_process_file(30, 'cmdline', content='baz\x00bza\x00')
        self.make_process_file(40, 'cmdline', content='something\x00else\x00')
        iterator = get_process_iterator(
            proc=self.tempdir.path, name_regexps=['foo', 'baz'])
        self.assertCountEqual([process.pid for process in iterator], [10, 30])

    def test_process_iterator_empty(self):
        """If no args are specified, an empty iterator is returned."""
        self.assertEqual([], list(get_process_iterator()))
