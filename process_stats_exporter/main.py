# Expose a Prometheus metrics endpoint with process stats.

from itertools import chain

from prometheus_aioexporter.script import PrometheusExporterScript

from lxstats.process import (
    Collection,
    Collector,
    CommandLineFilter)

from .stats import (
    ProcessStatsCollector,
    ProcessTasksStatsCollector)


class ProcessStatsExporter(PrometheusExporterScript):
    """Prometheus exporter script for process statistics."""

    name = 'process-stats-exporter'

    def configure_argument_parser(self, parser):
        parser.add_argument(
            '-i', '--interval', type=int, default=10,
            help='stats update interval')
        parser.add_argument(
            '-P', '--pids', nargs='+', type=int, metavar='pid',
            help='process PID')
        parser.add_argument(
            '-R', '--name-regexps', nargs='+',
            metavar='name-regexp', help='regexp to match process name')

    def configure(self, args):
        self._pids = args.pids
        self._name_regexps = args.name_regexps
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

        metric_configs = ProcessStatsCollector.metrics()
        metric_configs.extend(ProcessTasksStatsCollector.metrics())
        self._metrics = self.create_metrics(metric_configs)

    async def on_application_startup(self, application):
        # setup handler to update metrics on requests
        application.set_metric_update_handler(self._update_metrics)

    def _update_metrics(self, metrics):
        """Update metrics on requests."""
        for process in self._get_process_iterator():
            metric_values = ProcessStatsCollector.collect(process)
            metric_values.update(ProcessTasksStatsCollector.collect(process))
            for metric, value in metric_values.items():
                self._update_metric(process, metric, value)

    def _get_process_iterator(self):
        """Return an iterator yielding Process objects."""
        if self._pids:
            return Collection(collector=Collector(pids=self._pids))
        elif self._name_regexps:
            collections = []
            for name_re in self._name_regexps:
                collection = Collection()
                collection.add_filter(CommandLineFilter(name_re))
                collections.append(collection)
            return chain(*collections)
        else:
            return iter(())

    def _update_metric(self, process, metric_name, value):
        """Update the value for a metrics."""
        if value is None:
            self.logger.warning(
                'emtpy value for metric "{}" on PID {}'.format(
                    metric_name, process.pid))
            return

        metric = self._metrics[metric_name].labels(cmd=process.get('comm'))
        if metric._type == 'counter':
            metric.inc(value)
        elif metric._type == 'gauge':
            metric.set(value)


script = ProcessStatsExporter()
