
# doctable.parallel

This module was designed to manage worker processes and pipes with custom exception handling and methods to capture statistics indicating worker starvation and uptime. It was intended to be used when working with a single worker processs accessed through `WorkerResource` or multiple workers that receive data asynchronously accessed through `WorkerPool` (which works much like `multiprocessing.Pool`).

To make this work, I defined a bunch of custom messages for passing user functions, data payloads, user function exceptions, worker statistics, and other data.

1. A `WorkerResource` object is created that will launch a process with `target=Worker`, which contains information about a user function and any static data relevant to its use. Ideally this class is used as a context manager so that the workers will die when the program ends - otherwise use `.join()` or `.terminate()` to end the worker before your program exits.

2. A number of different messages can be sent to the worker process. Here are some:

    + `.update_userfunc()` to update the user function that the worker executes upon receiving data.

    + `.execute()` to send data to the worker process which will apply the user function and then send the result to the main process so it can be returned. This method is synchronous, so it will block until data is received or an exception is raised in the user function.

    + `.send_data()` to send data to the worker process which will apply the user function and return a result that can be retreived via `.recv_data()`. This is asynchronous, so it will not block and will queue results in a `multiprocessing.Pipe`.

    + `.poll()` to check if data can be retreived via `.recv_data()`.

    + `.recv_data()` to retrieve output from user function that was sent from the `Worker` after `.send_data()` was used to send.

    + `.get_status()` to request and return a `WorkerStatus` object that contains information like worker uptime, time spent applying user function to data, and time spent waiting for data from main process.
