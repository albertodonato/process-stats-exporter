from textwrap import dedent

from lxstats.process import Process
import pytest

from ..stats import (
    ProcessStatsCollector,
    ProcessTasksStatsCollector,
    StatsCollector,
)


class TestStatsCollector:

    def test_labels_empty(self):
        """By default, no label is applied."""
        collector = StatsCollector()
        assert collector.labels == []

    def test_labels(self):
        """Extra labels are saved."""
        collector = StatsCollector(['l1', 'l2'])
        assert collector.labels == ['l1', 'l2']

    def test_metrics(self):
        """The metrics() method must be implemented by subclasses."""
        with pytest.raises(NotImplementedError):
            StatsCollector().metrics()

    def test_collect(self):
        """The collect() method must be implemented by subclasses."""
        with pytest.raises(NotImplementedError):
            StatsCollector().collect(None)


class TestProcessStatsCollector:

    def test_metrics(self):
        """The list of process metrics is returned."""
        metrics = ProcessStatsCollector().metrics()
        assert [metric.name for metric in metrics] == [
            'proc_time_user', 'proc_time_system', 'proc_mem_rss',
            'proc_mem_rss_max', 'proc_maj_fault', 'proc_min_fault',
            'proc_ctx_involuntary', 'proc_ctx_voluntary'
        ]

    def test_collect(self, make_process_dir):
        """Stats for a process can be collected."""
        process_dir = make_process_dir(10)
        (process_dir / 'stat').write_text(' '.join(str(i) for i in range(45)))
        (process_dir / 'status').write_text('VmHWM: 100 kB')
        (process_dir / 'sched').write_text(
            dedent(
                '''\
                nr_involuntary_switches : 1000
                nr_voluntary_switches : 2000
                '''))
        process = Process(10, process_dir)
        assert ProcessStatsCollector().collect(process) == {
            'proc_time_user': 13,
            'proc_time_system': 14,
            'proc_mem_rss': 23,
            'proc_mem_rss_max': 102400,
            'proc_maj_fault': 11,
            'proc_min_fault': 9,
            'proc_ctx_involuntary': 1000,
            'proc_ctx_voluntary': 2000
        }


class TestProcessTasksStatsCollector:

    def test_metrics(self):
        """The list of process metrics is returned."""
        metrics = ProcessTasksStatsCollector().metrics()
        assert [metric.name for metric in metrics], [
            'proc_tasks_count', 'proc_tasks_state_running',
            'proc_tasks_state_sleeping',
            'proc_tasks_state_uninterruptible_sleep'
        ]

    def test_collect(self, make_process_dir):
        """Stats for process tasks can be collected."""
        process_dir = make_process_dir(10)
        (process_dir / 'task/123').mkdir(parents=True)
        (process_dir / 'task/123/stat').write_text('1 2 D')
        (process_dir / 'task/456').mkdir(parents=True)
        (process_dir / 'task/456/stat').write_text('1 2 R')
        (process_dir / 'task/789').mkdir(parents=True)
        (process_dir / 'task/789/stat').write_text('1 2 R')
        process = Process(10, process_dir)
        assert ProcessTasksStatsCollector().collect(process), {
            'proc_tasks_count': 3,
            'proc_tasks_state_running': 2,
            'proc_tasks_state_sleeping': 0,
            'proc_tasks_state_uninterruptible_sleep': 1
        }
