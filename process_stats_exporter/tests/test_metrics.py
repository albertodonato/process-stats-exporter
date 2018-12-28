import logging
import re

from lxstats.process import Process
from prometheus_aioexporter.metric import MetricsRegistry
import pytest

from ..label import (
    CmdlineLabeler,
    PidLabeler,
)
from ..metrics import ProcessMetricsHandler


@pytest.fixture
def labelers_processes():
    yield []


@pytest.fixture
def handler(labelers_processes):
    yield ProcessMetricsHandler(
        logging.getLogger('test'),
        pids=['10', '20'],
        get_process_iterator=lambda **kwargs: labelers_processes)


def get_samples(metric):
    """Return tuples with (labels, value) for a metric."""
    return sorted(
        (value, labels) for prefix, labels, value in metric._samples()
        if prefix == '_total')


class TestProcessMetricsHandler:

    def test_get_metric_configs(self, handler):
        """MetricConfigs are returned for process metrics."""
        metric_configs = handler.get_metric_configs()
        assert sorted(config.name for config in metric_configs) == [
            'proc_ctx_involuntary', 'proc_ctx_voluntary', 'proc_maj_fault',
            'proc_mem_rss', 'proc_mem_rss_max', 'proc_min_fault',
            'proc_tasks_count', 'proc_tasks_state_running',
            'proc_tasks_state_sleeping',
            'proc_tasks_state_uninterruptible_sleep', 'proc_time_system',
            'proc_time_user'
        ]

    def test_get_metric_configs_with_pids(self, handler):
        """If PIDs are specified, metrics include a "pid" label."""
        for metric in handler.get_metric_configs():
            assert metric.config['labels'] == ['pid']

    def test_update_metrics(self, make_process_dir, labelers_processes):
        """Metrics are updated with values from procesess."""
        process_10_dir = make_process_dir(10)
        (process_10_dir / 'comm').write_text('exec1')
        (process_10_dir / 'stat').write_text(
            ' '.join(str(i) for i in range(45)))
        (process_10_dir / 'task').mkdir()
        process_20_dir = make_process_dir(20)
        (process_20_dir / 'comm').write_text('exec2')
        (process_20_dir / 'stat').write_text(
            ' '.join(str(i) for i in range(45, 90)))
        (process_20_dir / 'task').mkdir()
        labelers_processes.extend(
            [
                (
                    CmdlineLabeler(re.compile('exec.*')),
                    Process(10, process_10_dir)),
                (
                    CmdlineLabeler(re.compile('exec.*')),
                    Process(20, process_20_dir))
            ])

        handler = ProcessMetricsHandler(
            logging.getLogger('test'),
            cmdline_regexps=[re.compile('exec.*')],
            get_process_iterator=lambda **kwargs: labelers_processes)
        metrics = MetricsRegistry().create_metrics(
            handler.get_metric_configs())
        handler.update_metrics(metrics)
        # check value of a sample metric
        metric = metrics['proc_min_fault']
        assert get_samples(metric) == [
            (9.0, {
                'cmd': 'exec1'
            }), (54.0, {
                'cmd': 'exec2'
            })
        ]

    def test_update_metrics_with_pids(
            self, make_process_dir, labelers_processes):
        """Metrics include the "pid" label if PIDs are specified."""
        process_10_dir = make_process_dir(10)
        process_20_dir = make_process_dir(20)
        labelers_processes.extend(
            [
                (PidLabeler(), Process(10, process_10_dir)),
                (PidLabeler(), Process(20, process_20_dir))
            ])
        handler = ProcessMetricsHandler(
            logging.getLogger('test'),
            pids=['10', '20'],
            get_process_iterator=lambda **kwargs: labelers_processes)
        (process_10_dir / 'comm').write_text('exec1')
        (process_10_dir / 'stat').write_text(
            ' '.join(str(i) for i in range(45)))
        (process_10_dir / 'task').mkdir()
        (process_20_dir / 'comm').write_text('exec2')
        (process_20_dir / 'stat').write_text(
            ' '.join(str(i) for i in range(45, 90)))
        (process_20_dir / 'task').mkdir()
        metrics = MetricsRegistry().create_metrics(
            handler.get_metric_configs())
        handler.update_metrics(metrics)
        # check value of a sample metric
        metric = metrics['proc_min_fault']
        [(_, labels1), (_, labels2)] = get_samples(metric)
        assert labels1['pid'] == '10'
        assert labels2['pid'] == '20'

    def test_log_empty_values(
            self, caplog, make_process_dir, handler, labelers_processes):
        """A message is logged for empty metric values."""
        caplog.set_level(logging.DEBUG)

        process_dir = make_process_dir(10)
        (process_dir / 'task').mkdir()
        labelers_processes.extend([(PidLabeler(), Process(10, process_dir))])
        metrics = MetricsRegistry().create_metrics(
            handler.get_metric_configs())
        handler.update_metrics(metrics)
        assert (
            'empty value for metric "proc_time_system" on PID 10' in caplog.
            messages)
