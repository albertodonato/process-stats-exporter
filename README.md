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

* using regexps for process command lines:

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

If PIDs are passed to the command line (e.g. `-P 1345 4921`), metrics are
tagged with a `"pid"` label, with the PID of each matched process:

```
process_mem_rss{pid="1345"} 1726.0
process_mem_rss{pid="4921"} 4439.0
```

When regexps are passed to match processes command line, labels are added based
on the regexp:

* if the regexp contains named groups (e.g. `-R '^(?P<exe>.*sh) '`), labels
  mapping the group name to match values are added:
  
```
process_mem_rss{exe="/bin/bash"} 1726.0
process_mem_rss{exe="/bin/sh"} 4439.0
```

* if the regexp contains unnamed groups, (e.g. `-R '^(.*sh) '`), `match_<N>`
  labels are added with match values:
  
```
process_mem_rss{match_1="/bin/bash"} 1726.0
process_mem_rss{match_1="/bin/sh"} 4439.0
```

* if the regexp contains no group (e.g. `-R sh`), a `"cmd"` label with the
  process `comm` name is used:

```
process_mem_rss{cmd="bash"} 1726.0
process_mem_rss{cmd="sh"} 4439.0
```

Additional static labels can be passed with the `-l` flag to tag all metrics (e.g. `-l foo=bar`):

```
process_mem_rss{pid="1345",foo="bar"} 1726.0
process_mem_rss{pid="4921",foo="bar"} 4439.0
```
