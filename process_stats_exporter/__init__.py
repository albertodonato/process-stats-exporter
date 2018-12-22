"""Export Prometheus metrics for processes and tasks."""

from distutils.version import LooseVersion

import pkg_resources

__all__ = ['__version__']

__version__ = LooseVersion(
    pkg_resources.require('process_stats_exporter')[0].version)
