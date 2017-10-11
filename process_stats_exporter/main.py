"""Expose a Prometheus metrics endpoint with process stats."""

from prometheus_aioexporter.script import PrometheusExporterScript

from .metrics import ProcessMetricsHandler
from .cmdline import LabelAction


class ProcessStatsExporter(PrometheusExporterScript):
    """Prometheus exporter script for process statistics."""

    name = 'process-stats-exporter'

    def configure_argument_parser(self, parser):
        parser.add_argument(
            '-P', '--pids', nargs='+', type=int, metavar='pid',
            help='process PID')
        parser.add_argument(
            '-R', '--cmdline-regexps', nargs='+',
            metavar='regexp', help='regexp to match process command line')
        parser.add_argument(
            '-l', '--labels', nargs='+', action=LabelAction, metavar='label',
            default={},
            help='add static label to all metrics (as "name=value")')

    def configure(self, args):
        if args.pids:
            self.logger.info(
                'tracking stats for PIDs [{}]'.format(
                    ', '.join(str(pid) for pid in args.pids)))
        elif args.cmdline_regexps:
            self.logger.info(
                'tracking stats for processes matching regexps [{}]'.format(
                    ', '.join(args.cmdline_regexps)))
        else:
            self.exit('Error: no PID or process names specified')

        self._metric_handler = ProcessMetricsHandler(
            logger=self.logger, pids=args.pids,
            cmdline_regexps=args.cmdline_regexps, labels=args.labels)
        self.create_metrics(self._metric_handler.get_metric_configs())

    async def on_application_startup(self, application):
        # setup handler to update metrics on requests
        application.set_metric_update_handler(
            self._metric_handler.update_metrics)


script = ProcessStatsExporter()
