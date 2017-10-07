# process-stats-exporter - Export process and task stats Prometheus metrics

[![Build Status](https://travis-ci.org/albertodonato/process-stats-exporter.svg?branch=master)](https://travis-ci.org/albertodonato/process-stats-exporter)
[![Coverage Status](https://codecov.io/gh/albertodonato/process-stats-exporter/branch/master/graph/badge.svg)](https://codecov.io/gh/albertodonato/process-stats-exporter)

`process-stats-exporter` is a [Prometheus](https://prometheus.io/) exporter
which collect metrics for processes and tasks.

# Running

`process-stats-exporter` can be given a set of processes to monitor in one of two ways:

* by giving a set of PIDs:

```bash
process-stats-exporter -P 123 456 789
```

* using regexps for process names:

```bash
process-stats-exporter -R 'foo.*' bar
```


# Metrics

Stats are accessible by default on `http://localhost:9090/metrics` (port can
be changed with the `-p` option).

Metrics are tagged with the command name, to allow filtering series, e.g.:

```bash
process_mem_rss{cmd="bash"} 1726.0
```
