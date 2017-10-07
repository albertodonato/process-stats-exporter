import os
from textwrap import dedent
from unittest import TestCase

from lxstats.testing import TestCase as LxStatsTestCase
from lxstats.process import Process

from ..stats import (
    StatsCollector,
    ProcessStatsCollector,
    ProcessTasksStatsCollector)


class StatsCollectorTests(TestCase):

    def test_metrics(self):
        """The metrics() method must be implemented by subclasses."""
        self.assertRaises(NotImplementedError, StatsCollector.metrics)

    def test_collect(self):
        """The collect() method must be implemented by subclasses."""
        self.assertRaises(NotImplementedError, StatsCollector.collect, None)


class ProcessStatsCollectorTests(LxStatsTestCase):

    def test_metrics(self):
        """The list of process metrics is returned."""
        metrics = ProcessStatsCollector.metrics()
        self.assertEqual(
            [metric.name for metric in metrics],
            ['process_time_user',
             'process_time_system',
             'process_mem_rss',
             'process_maj_fault',
             'process_min_fault',
             'process_ctx_involuntary',
             'process_ctx_voluntary',
             'process_mem_rss_max'])

    def test_collect(self):
        """Stats for a process can be collected."""
        pid = 10
        process = Process(pid, os.path.join(self.tempdir.path, str(pid)))
        self.make_process_file(
            pid, 'stat', content=' '.join(str(i) for i in range(45)))
        self.make_process_file(pid, 'status', content='VmHWM: 100 kB')
        self.make_process_file(
            pid, 'sched',
            content=dedent(
                '''\
                nr_involuntary_switches : 1000
                nr_voluntary_switches : 2000
                '''))
        self.assertEqual(
            ProcessStatsCollector.collect(process),
            {'process_time_system': 14,
             'process_mem_rss_max': 102400,
             'process_mem_rss': 23,
             'process_ctx_voluntary': 2000,
             'process_time_user': 13,
             'process_min_fault': 9,
             'process_ctx_involuntary': 1000,
             'process_maj_fault': 11})


class ProcessTasksStatsCollectorTests(LxStatsTestCase):

    def test_metrics(self):
        """The list of process metrics is returned."""
        metrics = ProcessTasksStatsCollector.metrics()
        self.assertEqual(
            [metric.name for metric in metrics],
            ['process_tasks_count',
             'process_tasks_state_running',
             'process_tasks_state_sleeping',
             'process_tasks_state_uninterruptible_sleep'])

    def test_collect(self):
        """Stats for process tasks can be collected."""
        pid = 10
        process_dir = os.path.join(self.tempdir.path, str(pid))
        process = Process(pid, process_dir)
        self.make_process_dir(pid, 'task/123')
        self.make_process_dir(pid, 'task/456')
        self.make_process_dir(pid, 'task/789')
        self.tempdir.mkfile(
            path='{}/task/123/stat'.format(pid),
            content='1 2 D')
        self.tempdir.mkfile(
            path='{}/task/456/stat'.format(pid),
            content='1 2 R')
        self.tempdir.mkfile(
            path='{}/task/789/stat'.format(pid),
            content='1 2 R')
        self.assertEqual(
            ProcessTasksStatsCollector.collect(process),
            {'process_tasks_count': 3,
             'process_tasks_state_running': 2,
             'process_tasks_state_sleeping': 0,
             'process_tasks_state_uninterruptible_sleep': 1})
