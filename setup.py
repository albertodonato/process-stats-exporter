from setuptools import setup, find_packages

from process_stats_exporter import __version__, __doc__ as description

tests_require = ['toolrack']

config = {
    'name': 'process-stats-exporter',
    'version': __version__,
    'license': 'GPLv3+',
    'description': description,
    'long_description': open('README.md').read(),
    'author': 'Alberto Donato',
    'author_email': 'alberto.donato@gmail.com',
    'maintainer': 'Alberto Donato',
    'maintainer_email': 'alberto.donato@gmail.com',
    'url': 'https://github.com/albertodonato/process-stats-exporter',
    'packages': find_packages(),
    'include_package_data': True,
    'entry_points': {'console_scripts': [
        'process-stats-exporter = process_stats_exporter.main:script']},
    'test_suite': 'process_stats_exporter',
    'install_requires': [
        'lxstats',
        'prometheus_aioexporter'],
    'tests_require': tests_require,
    'extras_require': {'testing': tests_require},
    'keywords': 'metric prometheus process exporter',
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities']}

setup(**config)
