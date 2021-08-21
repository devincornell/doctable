
# doctable.monitor

This module is in development, but was intended to serve as a local server for displaying logging information from a running script.


## Main Inferface

### doctable.monitor.Monitor

The interface to the monitor would look like this.

1. launch worker process

2. send update messages to the worker process when certain steps in the program have completed

For example, it might look like this:

```
monitor = doctable.Monitor(port=8888)

monitor.log('reading data from file')
with open('random.txt', 'r') as f:
    text = f.read()

monitor.log('parsing text')
lines = text.split()

monitor.log('finished')
```

## Worker process

The worker process will be started by the main script process at Monitor.__init__(), and it will take care of the following responsibilities.

1. Host an http server on the requested port that can display system and logging information. This could include any plots that can be created from timing data, etc.

2. Receive log messages from `Monitor` and record them for display in server.

3. Routinely record timing + cpu/memory recording for display in the server.


