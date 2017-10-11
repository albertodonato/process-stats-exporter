# process-stats-exporter - Export process and task stats Prometheus metrics

[![Build Status](https://travis-ci.org/albertodonato/process-stats-exporter.svg?branch=master)](https://travis-ci.org/albertodonato/process-stats-exporter)
[![Coverage Status](https://codecov.io/gh/albertodonato/process-stats-exporter/branch/master/graph/badge.svg)](https://codecov.io/gh/albertodonato/process-stats-exporter)

`process-stats-exporter` is a [Prometheus](https://prometheus.io/) exporter
which collect metrics for processes and tasks.

## Running

`process-stats-exporter` can be given a set of processes to monitor in one of two ways:

* by giving a set of PIDs:

```bash
process-stats-exporter -P 123 456 789
```

* using regexps for process names:

```bash
process-stats-exporter -R 'foo.*' bar
```


## Metrics

Process stats are accessible by default on `http://localhost:9090/metrics`
(port can be changed with the `-p` option).

The following metrics are currently available:

* `process_time_user`: time scheduled in user mode
* `process_time_system`: time scheduled in kernel mode
* `process_mem_rss`: memory resident segment size (RSS)
* `process_mem_rss_max`: maximum memory resident segment size (RSS)
* `process_maj_fault`: number of major faults that required a page load
* `process_min_fault`: number of minor faults that did not require a page load
* `process_ctx_involuntary` number of involuntary context switches
* `process_ctx_voluntary`: number of voluntary context switches
* `process_tasks_count`: number of tasks for a process
* `process_tasks_state_running`: number of process tasks in running state
* `process_tasks_state_sleeping`: number of process tasks in sleeping state
* `process_tasks_state_uninterruptible_sleep`: number of process tasks in
  uninterruptible sleep state


### Labels

All metrics are labeled with the command name, to allow filtering series, e.g.:

```
process_mem_rss{cmd="bash"} 1726.0
```

Additional static labels can be passed with the `-l` flag to tag all metrics (e.g. `-l foo=bar`):

```
process_mem_rss{cmd="bash",foo="bar"} 1726.0
```
