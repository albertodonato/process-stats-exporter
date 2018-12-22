from textwrap import dedent
from unittest import TestCase

from lxstats.process import Process
from lxstats.testing import TestCase as LxStatsTestCase

from ..stats import (
    ProcessStatsCollector,
    ProcessTasksStatsCollector,
    StatsCollector,
)


class StatsCollectorTests(TestCase):

    def test_labels_empty(self):
        """By default, no label is applied."""
        collector = StatsCollector()
        self.assertEqual(collector.labels, [])

    def test_labels(self):
        """Extra labels are saved."""
        collector = StatsCollector(['l1', 'l2'])
        self.assertEqual(collector.labels, ['l1', 'l2'])

    def test_metrics(self):
        """The metrics() method must be implemented by subclasses."""
        self.assertRaises(NotImplementedError, StatsCollector().metrics)

    def test_collect(self):
        """The collect() method must be implemented by subclasses."""
        self.assertRaises(NotImplementedError, StatsCollector().collect, None)


class ProcessStatsCollectorTests(LxStatsTestCase):

    def setUp(self):
        super().setUp()
        self.collector = ProcessStatsCollector()

    def test_metrics(self):
        """The list of process metrics is returned."""
        metrics = self.collector.metrics()
        self.assertEqual(
            [metric.name for metric in metrics], [
                'proc_time_user', 'proc_time_system', 'proc_mem_rss',
                'proc_mem_rss_max', 'proc_maj_fault', 'proc_min_fault',
                'proc_ctx_involuntary', 'proc_ctx_voluntary'
            ])

    def test_collect(self):
        """Stats for a process can be collected."""
        pid = 10
        process = Process(pid, self.tempdir.path / str(pid))
        self.make_process_file(
            pid, 'stat', content=' '.join(str(i) for i in range(45)))
        self.make_process_file(pid, 'status', content='VmHWM: 100 kB')
        self.make_process_file(
            pid,
            'sched',
            content=dedent(
                '''\
                nr_involuntary_switches : 1000
                nr_voluntary_switches : 2000
                '''))
        self.assertEqual(
            self.collector.collect(process), {
                'proc_time_user': 13,
                'proc_time_system': 14,
                'proc_mem_rss': 23,
                'proc_mem_rss_max': 102400,
                'proc_maj_fault': 11,
                'proc_min_fault': 9,
                'proc_ctx_involuntary': 1000,
                'proc_ctx_voluntary': 2000
            })


class ProcessTasksStatsCollectorTests(LxStatsTestCase):

    def setUp(self):
        super().setUp()
        self.collector = ProcessTasksStatsCollector()

    def test_metrics(self):
        """The list of process metrics is returned."""
        metrics = self.collector.metrics()
        self.assertEqual(
            [metric.name for metric in metrics], [
                'proc_tasks_count', 'proc_tasks_state_running',
                'proc_tasks_state_sleeping',
                'proc_tasks_state_uninterruptible_sleep'
            ])

    def test_collect(self):
        """Stats for process tasks can be collected."""
        pid = 10
        process_dir = self.tempdir.path / str(pid)
        process = Process(pid, process_dir)
        self.make_process_dir(pid, 'task/123')
        self.make_process_dir(pid, 'task/456')
        self.make_process_dir(pid, 'task/789')
        self.tempdir.mkfile(
            path='{}/task/123/stat'.format(pid), content='1 2 D')
        self.tempdir.mkfile(
            path='{}/task/456/stat'.format(pid), content='1 2 R')
        self.tempdir.mkfile(
            path='{}/task/789/stat'.format(pid), content='1 2 R')
        self.assertEqual(
            self.collector.collect(process), {
                'proc_tasks_count': 3,
                'proc_tasks_state_running': 2,
                'proc_tasks_state_sleeping': 0,
                'proc_tasks_state_uninterruptible_sleep': 1
            })
