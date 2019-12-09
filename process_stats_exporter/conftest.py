from pathlib import Path

import pytest


@pytest.fixture
def proc_dir(tmpdir):
    """A /proc path."""
    path = Path(tmpdir / "proc")
    path.mkdir()
    yield path


@pytest.fixture
def make_process_dir(proc_dir):
    """Return a function to create /proc/<pid> dir for a process."""

    def create(pid):
        pid_dir = proc_dir / str(pid)
        pid_dir.mkdir()
        return pid_dir

    yield create
