import re

from ..label import (
    CmdlineLabeler,
    PidLabeler,
)
from ..process import get_process_iterator


class TestGetProcessIterator:
    def test_process_iterator_pids(self, proc_dir, make_process_dir):
        """An iterator yielding processes with specified PIDs is returned."""
        (make_process_dir(10) / "cmdline").write_text("cmd")
        (make_process_dir(20) / "cmdline").write_text("cmd")
        (make_process_dir(30) / "cmdline").write_text("cmd")
        (make_process_dir(40) / "cmdline").write_text("cmd")
        iterator = get_process_iterator(proc=proc_dir, pids=[10, 30])
        labelers, processes = zip(*iterator)
        for labeler in labelers:
            assert isinstance(labeler, PidLabeler)
        assert sorted(process.pid for process in processes) == [10, 30]

    def test_process_iterator_cmdline_regexps(self, proc_dir, make_process_dir):
        """An iterator yielding processes with matching cmdline is returned."""
        (make_process_dir(10) / "cmdline").write_text("foo\x00bar\x00")
        (make_process_dir(20) / "cmdline").write_text("another\x00command\x00")
        (make_process_dir(30) / "cmdline").write_text("baz\x00bza\x00")
        (make_process_dir(40) / "cmdline").write_text("something\x00else\x00")
        iterator = get_process_iterator(
            proc=proc_dir, cmdline_regexps=[re.compile("foo"), re.compile("baz")]
        )
        labelers, processes = zip(*iterator)
        for labeler in labelers:
            assert isinstance(labeler, CmdlineLabeler)
        assert sorted(process.pid for process in processes) == [10, 30]

    def test_process_iterator_cmdline_regexps_matches_args(
        self, proc_dir, make_process_dir
    ):
        """Cmdline regexps match the full cmdline"""
        (make_process_dir(10) / "cmdline").write_text("foo\x00bar\x00")
        (make_process_dir(20) / "cmdline").write_text("another\x00command\x00")
        iterator = get_process_iterator(
            proc=proc_dir, cmdline_regexps=[re.compile("bar")]
        )
        _, processes = zip(*iterator)
        assert [process.pid for process in processes] == [10]

    def test_process_iterator_empty(self):
        """If no args are specified, an empty iterator is returned."""
        assert list(get_process_iterator()) == []
