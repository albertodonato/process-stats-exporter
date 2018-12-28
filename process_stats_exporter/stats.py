"""Collect metrics for processes and tasks"""

from collections import defaultdict
from typing import (
    Any,
    DefaultDict,
    List,
    Mapping,
    NamedTuple,
    Sequence,
)

from lxstats.process import Process
from prometheus_aioexporter import MetricConfig


class ProcessStat(NamedTuple):
    """Definition for a process statistic."""

    metric: str
    type: str
    description: str
    stat: str


class ProcessTasksStat(NamedTuple):
    """Definition for a process task statistic."""

    metric: str
    type: str
    description: str


class StatsCollector:
    """Describe and collect metrics."""

    def __init__(self, labels: Sequence[str] = ()):
        self.labels = list(labels)

    def metrics(self) -> List[MetricConfig]:
        """Return a list of MetricConfigs."""
        raise NotImplementedError('Subclasses must implement metrics()')

    def collect(self, process: Process) -> Mapping[str, Any]:
        """Return a dict mapping metric names to values for the process."""
        raise NotImplementedError('Subclasses must implement collect()')


class ProcessStatsCollector(StatsCollector):
    """Collect metrics for a process."""

    _STATS = (
        ProcessStat(
            'proc_time_user', 'counter', 'Time scheduled in user mode',
            'stat.utime'),
        ProcessStat(
            'proc_time_system', 'counter', 'Time scheduled in kernel mode',
            'stat.stime'),
        ProcessStat(
            'proc_mem_rss', 'gauge', 'Memory resident segment size (RSS)',
            'stat.rss'),
        ProcessStat(
            'proc_mem_rss_max', 'counter',
            'Maximum memory resident segment size (RSS)', 'status.VmHWM'),
        ProcessStat(
            'proc_maj_fault', 'counter',
            'Number of major faults that required a page load', 'stat.majflt'),
        ProcessStat(
            'proc_min_fault', 'counter',
            'Number of minor faults that did not require a page load',
            'stat.minflt'),
        ProcessStat(
            'proc_ctx_involuntary', 'counter',
            'Number of involuntary context switches',
            'sched.nr_involuntary_switches'),
        ProcessStat(
            'proc_ctx_voluntary', 'counter',
            'Number of voluntary context switches',
            'sched.nr_voluntary_switches'))

    def metrics(self) -> List[MetricConfig]:
        return [
            MetricConfig(
                stat.metric, stat.description, stat.type,
                {'labels': self.labels}) for stat in self._STATS
        ]

    def collect(self, process: Process) -> Mapping[str, Any]:
        process.collect_stats()
        return {stat.metric: process.get(stat.stat) for stat in self._STATS}


class ProcessTasksStatsCollector(StatsCollector):
    """Collect metrics for a process' tasks."""

    _STATS = (
        ProcessTasksStat(
            'proc_tasks_count', 'gauge', 'Number of process tasks'),
        ProcessTasksStat(
            'proc_tasks_state_running', 'gauge',
            'Number of process tasks in running state'),
        ProcessTasksStat(
            'proc_tasks_state_sleeping', 'gauge',
            'Number of process tasks in sleeping state'),
        ProcessTasksStat(
            'proc_tasks_state_uninterruptible_sleep', 'gauge',
            'Number of process tasks in uninterruptible sleep state'),
    )

    def metrics(self) -> List[MetricConfig]:
        return [
            MetricConfig(
                stat.metric, stat.description, stat.type,
                {'labels': self.labels}) for stat in self._STATS
        ]

    def collect(self, process: Process) -> Mapping[str, int]:
        tasks = process.tasks()
        state_counts: DefaultDict[str, int] = defaultdict(int)
        for task in tasks:
            task.collect_stats()
            state_id: str = task.get('stat.state')
            state_counts[state_id] += 1
        return {
            'proc_tasks_count': len(tasks),
            'proc_tasks_state_running': state_counts['R'],
            'proc_tasks_state_sleeping': state_counts['S'],
            'proc_tasks_state_uninterruptible_sleep': state_counts['D']
        }
