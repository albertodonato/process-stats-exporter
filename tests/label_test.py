import re

from lxstats.process import Process
import pytest

from process_stats_exporter.label import (
    CmdlineLabeler,
    PidLabeler,
)


class TestPidLabeler:
    def test_labels(self):
        """PidLabeler returns the "pid" label."""
        assert PidLabeler().labels() == {"pid"}

    def test_call(self):
        """The labeler returns a label with the process PID."""
        process = Process(10, "/proc/10")
        assert PidLabeler()(process) == {"pid": "10"}


class TestCmdlineLabeler:
    @pytest.mark.parametrize(
        "regex,labels",
        [
            (r"exec", {"cmd"}),
            (r"([0-9]+)exec([a-z]+)", {"match_1", "match_2"}),
            (r"(?P<foo>[0-9]+)exec(?P<bar>[a-z]+)", {"foo", "bar"}),
        ],
    )
    def test_labels(self, regex, labels):
        """Labels are created based on regexp groups."""
        labeler = CmdlineLabeler(re.compile(regex))
        assert labeler.labels() == labels

    def test_call(self, make_process_dir):
        """The labeler returns a label with the process "cmd"."""
        process_dir = make_process_dir(10)
        (process_dir / "comm").write_text("exec")
        process = Process(10, process_dir)
        process.collect_stats()
        labeler = CmdlineLabeler(re.compile("exec"))
        assert labeler(process) == {"cmd": "exec"}

    def test_call_with_groups(self, make_process_dir):
        """The labeler returns labels with regexp matches."""
        process_dir = make_process_dir(10)
        (process_dir / "cmdline").write_text("/path/to/exec")
        process = Process(10, process_dir)
        process.collect_stats()
        labeler = CmdlineLabeler(re.compile("(.*)/exec"))
        assert labeler(process) == {"match_1": "/path/to"}

    def test_call_with_named_groups(self, make_process_dir):
        """The labeler returns labels with named regexp matches."""
        process_dir = make_process_dir(10)
        (process_dir / "cmdline").write_text("/path/to/exec")
        process = Process(10, process_dir)
        process.collect_stats()
        labeler = CmdlineLabeler(re.compile("(?P<prefix>.*)/exec"))
        assert labeler(process) == {"prefix": "/path/to"}
