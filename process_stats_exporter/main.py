"""Expose a Prometheus metrics endpoint with process stats."""

from argparse import (
    ArgumentParser,
    Namespace,
)

from aiohttp.web import Application
from prometheus_aioexporter.script import PrometheusExporterScript

from .cmdline import (
    CmdlineRegexpAction,
    LabelAction,
)
from .metrics import ProcessMetricsHandler


class ProcessStatsExporter(PrometheusExporterScript):
    """Prometheus exporter script for process statistics."""

    name = "process-stats-exporter"

    def configure_argument_parser(self, parser: ArgumentParser):
        parser.add_argument(
            "-P",
            "--pids",
            nargs="+",
            type=int,
            metavar="pid",
            help="process PID",
        )
        parser.add_argument(
            "-R",
            "--cmdline-regexps",
            nargs="+",
            action=CmdlineRegexpAction,
            metavar="regexp",
            help="regexp to match process command line",
        )
        parser.add_argument(
            "-l",
            "--labels",
            nargs="+",
            action=LabelAction,
            metavar="label",
            default={},
            help='add static label to all metrics (as "name=value")',
        )

    def configure(self, args: Namespace):
        if args.pids:
            pidlist = ", ".join(str(pid) for pid in args.pids)
            self.logger.info(f"tracking stats for PIDs [{pidlist}]")
        elif args.cmdline_regexps:
            re_list = ", ".join(rexp.pattern for rexp in args.cmdline_regexps)
            self.logger.info(
                f"tracking stats for processes matching regexps [{re_list}]"
            )
        else:
            self.exit("Error: no PID or process names specified")

        self._metric_handler = ProcessMetricsHandler(
            logger=self.logger,
            pids=args.pids,
            cmdline_regexps=args.cmdline_regexps,
            labels=args.labels,
        )
        self.create_metrics(self._metric_handler.get_metric_configs())

    async def on_application_startup(self, application: Application):
        async def handler(metrics):
            self._metric_handler.update_metrics(metrics)

        application["exporter"].set_metric_update_handler(handler)


script = ProcessStatsExporter()
