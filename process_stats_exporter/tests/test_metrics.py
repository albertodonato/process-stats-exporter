import os
import logging
from operator import itemgetter

from fixtures import LoggerFixture

from prometheus_client import CollectorRegistry

from prometheus_aioexporter.metric import create_metrics

from lxstats.testing import TestCase
from lxstats.process import Process

from ..metrics import ProcessMetricsHandler


class ProcessMetricsHandlerTests(TestCase):

    def setUp(self):
        super().setUp()
        self.processes = []
        self.logger = self.useFixture(LoggerFixture(level=logging.DEBUG))
        self.handler = ProcessMetricsHandler(
            logging.getLogger('test'), labels={'foo': 'bar'},
            get_process_iterator=lambda **kwargs: self.processes)
        self.registry = CollectorRegistry()

    def test_get_metric_configs(self):
        """MetricConfigs are returned for process metrics."""
        metric_configs = self.handler.get_metric_configs()
        self.assertCountEqual(
            [config.name for config in metric_configs],
            ['process_ctx_involuntary', 'process_ctx_voluntary',
             'process_maj_fault', 'process_mem_rss', 'process_mem_rss_max',
             'process_min_fault', 'process_tasks_count',
             'process_tasks_state_running', 'process_tasks_state_sleeping',
             'process_tasks_state_uninterruptible_sleep',
             'process_time_system', 'process_time_user'])

    def test_update_metrics(self):
        """Metrics are updated with values from procesess."""
        self.processes = [
            Process(10, os.path.join(self.tempdir.path, '10')),
            Process(20, os.path.join(self.tempdir.path, '20'))]
        self.make_process_file(10, 'comm', content='exec1')
        self.make_process_file(
            10, 'stat', content=' '.join(str(i) for i in range(45)))
        self.make_process_dir(10, 'task')
        self.make_process_file(20, 'comm', content='exec2')
        self.make_process_file(
            20, 'stat', content=' '.join(str(i) for i in range(45, 90)))
        self.make_process_dir(20, 'task')
        metrics = create_metrics(
            self.handler.get_metric_configs(), self.registry)
        self.handler.update_metrics(metrics)
        # check value of a sample metric
        metric = metrics['process_min_fault']
        [(_, labels1, value1), (_, labels2, value2)] = sorted(
            metric._samples(), key=itemgetter(2))
        self.assertEqual(labels1, {'foo': 'bar', 'cmd': 'exec1'})
        self.assertEqual(value1, 9.0)
        self.assertEqual(labels2, {'foo': 'bar', 'cmd': 'exec2'})
        self.assertEqual(value2, 54.0)

    def test_log_empty_values(self):
        """A message is logged for empty metric values."""
        self.processes = [Process(10, os.path.join(self.tempdir.path, '10'))]
        self.make_process_dir(10, 'task')
        metrics = create_metrics(
            self.handler.get_metric_configs(), self.registry)
        self.handler.update_metrics(metrics)
        self.assertIn(
            'empty value for metric "process_time_system" on PID 10',
            self.logger.output)
