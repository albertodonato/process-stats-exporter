"""Expose a Prometheus metrics endpoint with process stats."""

from itertools import chain

from prometheus_aioexporter.script import PrometheusExporterScript

from .stats import (
    ProcessStatsCollector,
    ProcessTasksStatsCollector)
from .labels import LabelAction
from .process import get_process_iterator


class ProcessStatsExporter(PrometheusExporterScript):
    """Prometheus exporter script for process statistics."""

    name = 'process-stats-exporter'

    def configure_argument_parser(self, parser):
        parser.add_argument(
            '-P', '--pids', nargs='+', type=int, metavar='pid',
            help='process PID')
        parser.add_argument(
            '-R', '--name-regexps', nargs='+',
            metavar='name-regexp', help='regexp to match process name')
        parser.add_argument(
            '-l', '--labels', nargs='+', action=LabelAction, metavar='label',
            default={},
            help='add static label to all metrics (as "name=value")')

    def configure(self, args):
        self._pids = args.pids
        self._name_regexps = args.name_regexps
        self._labels = args.labels

        if self._pids:
            self.logger.info(
                'tracking stats for PIDs [{}]'.format(
                    ', '.join(str(pid) for pid in self._pids)))
        elif self._name_regexps:
            self.logger.info(
                'tracking stats for processes [{}]'.format(
                    ', '.join(self._name_regexps)))
        else:
            self.exit('Error: no PID or process names specified')

        self._setup_metrics()

    async def on_application_startup(self, application):
        # setup handler to update metrics on requests
        application.set_metric_update_handler(self._update_metrics)

    def _setup_metrics(self):
        """Setup collectors and related metrics."""
        labels = list(self._labels)
        self.collectors = [
            ProcessStatsCollector(labels=labels),
            ProcessTasksStatsCollector(labels=labels)]

        metric_configs = list(chain(
            *(collector.metrics() for collector in self.collectors)))
        self._metrics = self.create_metrics(metric_configs)

    def _update_metrics(self, metrics):
        """Update metrics on requests."""
        process_iter = get_process_iterator(
            pids=self._pids, name_regexps=self._name_regexps)
        for process in process_iter:
            metric_values = {}
            for collector in self.collectors:
                metric_values.update(collector.collect(process))
            for metric, value in metric_values.items():
                self._update_metric(process, metric, value)

    def _update_metric(self, process, metric_name, value):
        """Update the value for a metrics."""
        if value is None:
            self.logger.warning(
                'emtpy value for metric "{}" on PID {}'.format(
                    metric_name, process.pid))
            return

        labels = self._labels.copy()
        labels['cmd'] = process.get('comm')
        metric = self._metrics[metric_name].labels(**labels)
        if metric._type == 'counter':
            metric.inc(value)
        elif metric._type == 'gauge':
            metric.set(value)


script = ProcessStatsExporter()
