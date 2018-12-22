from pathlib import Path

from setuptools import (
    find_packages,
    setup,
)

tests_require = ['pytest']

config = {
    'name': 'process-stats-exporter',
    'version': '0.0.1',
    'license': 'GPLv3+',
    'description': 'Export Prometheus metrics for processes and tasks',
    'long_description': Path('README.rst').read_text(),
    'author': 'Alberto Donato',
    'author_email': 'alberto.donato@gmail.com',
    'maintainer': 'Alberto Donato',
    'maintainer_email': 'alberto.donato@gmail.com',
    'url': 'https://github.com/albertodonato/process-stats-exporter',
    'packages': find_packages(
        include=['process_stats_exporter', 'process_stats_exporter.*']),
    'include_package_data': True,
    'entry_points': {
        'console_scripts': [
            'process-stats-exporter = process_stats_exporter.main:script'
        ]
    },
    'test_suite': 'process_stats_exporter',
    'install_requires': ['lxstats', 'prometheus_aioexporter'],
    'tests_require': tests_require,
    'extras_require': {
        'testing': tests_require
    },
    'keywords': 'metric prometheus process exporter',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7', 'Topic :: Utilities'
    ]
}

setup(**config)
