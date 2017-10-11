"""Create and update metrics."""

from itertools import chain

from .stats import (
    ProcessStatsCollector,
    ProcessTasksStatsCollector)
from .process import get_process_iterator


class ProcessMetricsHandler:
    """Handle metrics for processes."""

    def __init__(self, logger, pids=None, name_regexps=None, labels=None,
                 get_process_iterator=get_process_iterator):
        self.logger = logger
        self._pids = pids
        self._name_regexps = name_regexps
        self._labels = labels or {}
        self._get_process_iterator = get_process_iterator

        label_names = self._get_label_names()
        self._collectors = [
            ProcessStatsCollector(labels=label_names),
            ProcessTasksStatsCollector(labels=label_names)]

    def get_metric_configs(self):
        """Return a list of MetricConfigs."""
        return list(chain(
            *(collector.metrics() for collector in self._collectors)))

    def update_metrics(self, metrics):
        """Update the specified metrics for processes."""
        process_iter = self._get_process_iterator(
            pids=self._pids, name_regexps=self._name_regexps)
        for process in process_iter:
            metric_values = {}
            for collector in self._collectors:
                metric_values.update(collector.collect(process))
            for name, metric in metrics.items():
                self._update_metric(process, name, metric, metric_values[name])

    def _update_metric(self, process, metric_name, metric, value):
        """Update the value for a metrics."""
        if value is None:
            self.logger.warning(
                'empty value for metric "{}" on PID {}'.format(
                    metric_name, process.pid))
            return

        metric = metric.labels(**self._get_labels(process))
        if metric._type == 'counter':
            metric.inc(value)
        elif metric._type == 'gauge':
            metric.set(value)

    def _get_label_names(self):
        """Return a list of label names."""
        labels = list(self._labels)
        labels.append('cmd')
        if self._pids:
            labels.append('pid')
        return labels

    def _get_labels(self, process):
        """Return labels for a process."""
        labels = self._labels.copy()
        labels['cmd'] = process.get('comm')
        if self._pids:
            labels['pid'] = str(process.pid)
        return labels
