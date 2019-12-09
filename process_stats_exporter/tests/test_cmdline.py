import argparse

import pytest

from ..cmdline import (
    CmdlineRegexpAction,
    LabelAction,
)


@pytest.fixture
def error_messages():
    yield []


@pytest.fixture
def label_parser(error_messages):
    parser = argparse.ArgumentParser()
    parser.add_argument("--labels", nargs="+", action=LabelAction)
    parser.error = error_messages.append
    yield parser


class TestLabelAction:
    def test_parse_labels(self, label_parser, error_messages):
        """LabelAction parses labels into a dict mapping names to values."""
        args = label_parser.parse_args(["--labels", "foo=bar", "baz=bza"])
        assert args.labels == {"foo": "bar", "baz": "bza"}
        assert error_messages == []

    def test_invalid_format(self, label_parser, error_messages):
        """If labels are not specified as name=value, an error is raised."""
        label_parser.parse_args(["--labels", "foobar"])
        assert error_messages == ['labels must be in the form "name=value": foobar']

    def test_invalid_name(self, label_parser, error_messages):
        """Invalid label names raise an error."""
        label_parser.parse_args(["--labels", "i am invalid=bar"])
        assert error_messages == ["invalid label: i am invalid"]


@pytest.fixture
def regexp_parser(error_messages):
    parser = argparse.ArgumentParser()
    parser.add_argument("--regexps", nargs="+", action=CmdlineRegexpAction)
    parser.error = error_messages.append
    yield parser


class TestCmdlineRegexpAction:
    def test_parse_regexps(self, regexp_parser, error_messages):
        """CmdlineRegexpAction parses and compiles strings into regexps."""
        args = regexp_parser.parse_args(["--regexps", ".*bash", "ls.*"])
        assert [regex.pattern for regex in args.regexps] == [".*bash", "ls.*"]
        assert error_messages == []

    def test_invalid_regexp(self, regexp_parser, error_messages):
        """If a regexp is malformed, an error is raised."""
        regexp_parser.parse_args(["--regexps", "(?P<wrong.*)"])
        assert error_messages == [
            "compiling regexp '(?P<wrong.*)': missing >, unterminated "
            "name at position 4"
        ]

    def test_invalid_regexp_group_name(self, regexp_parser, error_messages):
        """If a regexp group name is invalid as label, an error is raised."""
        regexp_parser.parse_args(["--regexps", "(?P<_invalid>.*)"])
        assert error_messages == ["regexp group not valid as label: _invalid"]
