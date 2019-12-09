"""Create and update metrics."""

from itertools import chain
from logging import Logger
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
)

from lxstats.process import Process
from prometheus_aioexporter import MetricConfig
from prometheus_client import Metric

from .label import (
    CmdlineLabeler,
    Labeler,
    PidLabeler,
)
from .process import (
    get_process_iterator,
    ProcessIteratorResult,
)
from .stats import (
    ProcessStatsCollector,
    ProcessTasksStatsCollector,
    StatsCollector,
)

ProcessIterator = Callable[..., ProcessIteratorResult]


class ProcessMetricsHandler:
    """Handle metrics for processes."""

    def __init__(
        self,
        logger: Logger,
        pids: Optional[List[str]] = None,
        cmdline_regexps: Optional[List[str]] = None,
        labels: Optional[Dict[str, str]] = None,
        get_process_iterator: ProcessIterator = get_process_iterator,
    ):
        self.logger = logger
        self._pids = pids or ()
        self._cmdline_regexps = cmdline_regexps or ()
        self._labels = labels or {}
        self._get_process_iterator = get_process_iterator

        label_names = self._get_label_names()
        self._collectors: List[StatsCollector] = [
            ProcessStatsCollector(labels=label_names),
            ProcessTasksStatsCollector(labels=label_names),
        ]

    def get_metric_configs(self) -> List[MetricConfig]:
        """Return a list of MetricConfigs."""
        return list(chain(*(collector.metrics() for collector in self._collectors)))

    def update_metrics(self, metrics: Dict[str, Metric]):
        """Update the specified metrics for processes."""
        process_iter = self._get_process_iterator(
            pids=self._pids, cmdline_regexps=self._cmdline_regexps
        )
        for labeler, process in process_iter:
            metric_values: Dict[str, Any] = {}
            for collector in self._collectors:
                metric_values.update(collector.collect(process))
            for name, metric in metrics.items():
                self._update_metric(labeler, process, name, metric, metric_values[name])

    def _update_metric(
        self,
        labeler: Labeler,
        process: Process,
        metric_name: str,
        metric: Metric,
        value: Any,
    ):
        """Update the value for a metrics."""
        if value is None:
            self.logger.warning(
                f'empty value for metric "{metric_name}" on PID {process.pid}'
            )
            return

        labels = self._labels.copy()
        labels.update(labeler(process))
        metric = metric.labels(**labels)
        if metric._type == "counter":
            metric.inc(value)
        elif metric._type == "gauge":
            metric.set(value)

    def _get_label_names(self) -> List[str]:
        """Return a set of label names."""
        labels = set(self._labels)
        for regexp in self._cmdline_regexps:
            labels.update(CmdlineLabeler(regexp).labels())
        if self._pids:
            labels.update(PidLabeler().labels())
        return list(labels)
