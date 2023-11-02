
import doctable.parallel
from .monitorworker import MonitorWorker


class Monitor:
    '''Maintains a monitor process to track program progress, memory usage, and messages.
    '''
    def __init__(self, port):
        self.worker = doctable.parallel.WorkerResource(
            target=MonitorWorker, 
            start=True, 
            logging=True, 
            verbose=False
        )



