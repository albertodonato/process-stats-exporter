"""Collect metrics for processes and tasks"""

from collections import (
    namedtuple,
    defaultdict)

from prometheus_aioexporter.metric import MetricConfig


ProcessStat = namedtuple(
    'ProcessStat', ['metric', 'type', 'description', 'stat'])

ProcessTasksStat = namedtuple(
    'ProcessTaskStat', ['metric', 'type', 'description'])


class StatsCollector:
    """Describe and collect metrics."""

    def __init__(self, labels=()):
        self.labels = list(labels)

    def metrics(self):
        """Return a list of MetricConfigs."""
        raise NotImplementedError('Subclasses must implement metrics()')

    def collect(self, process):
        """Return a dict mapping metric names to values for the process."""
        raise NotImplementedError('Subclasses must implement collect()')


class ProcessStatsCollector(StatsCollector):
    """Collect metrics for a process."""

    _STATS = (
        ProcessStat(
            'process_time_user', 'counter', 'Time scheduled in user mode',
            'stat.utime'),
        ProcessStat(
            'process_time_system', 'counter',
            'Time scheduled in kernel mode', 'stat.stime'),
        ProcessStat(
            'process_mem_rss', 'gauge', 'Memory resident segment size (RSS)',
            'stat.rss'),
        ProcessStat(
            'process_mem_rss_max', 'counter',
            'Maximum memory resident segment size (RSS)', 'status.VmHWM'),
        ProcessStat(
            'process_maj_fault', 'counter',
            'Number of major faults that required a page load', 'stat.majflt'),
        ProcessStat(
            'process_min_fault', 'counter',
            'Number of minor faults that did not require a page load',
            'stat.minflt'),
        ProcessStat(
            'process_ctx_involuntary', 'counter',
            'Number of involuntary context switches',
            'sched.nr_involuntary_switches'),
        ProcessStat(
            'process_ctx_voluntary', 'counter',
            'Number of voluntary context switches',
            'sched.nr_voluntary_switches'))

    def metrics(self):
        return [
            MetricConfig(
                stat.metric, stat.description, stat.type,
                {'labels': self.labels})
            for stat in self._STATS]

    def collect(self, process):
        process.collect_stats()
        return {stat.metric: process.get(stat.stat) for stat in self._STATS}


class ProcessTasksStatsCollector(StatsCollector):
    """Collect metrics for a process' tasks."""

    _STATS = (
        ProcessTasksStat(
            'process_tasks_count', 'gauge', 'Number of process tasks'),
        ProcessTasksStat(
            'process_tasks_state_running', 'gauge',
            'Number of process tasks in running state'),
        ProcessTasksStat(
            'process_tasks_state_sleeping', 'gauge',
            'Number of process tasks in sleeping state'),
        ProcessTasksStat(
            'process_tasks_state_uninterruptible_sleep', 'gauge',
            'Number of process tasks in uninterruptible sleep state'),
    )

    def metrics(self):
        return [
            MetricConfig(
                stat.metric, stat.description, stat.type,
                {'labels': self.labels})
            for stat in self._STATS]

    def collect(self, process):
        tasks = process.tasks()
        state_counts = defaultdict(int)
        for task in tasks:
            task.collect_stats()
            state_counts[task.get('stat.state')] += 1
        return {
            'process_tasks_count': len(tasks),
            'process_tasks_state_running': state_counts['R'],
            'process_tasks_state_sleeping': state_counts['S'],
            'process_tasks_state_uninterruptible_sleep': state_counts['D']}
