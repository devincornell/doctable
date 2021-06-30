
from multiprocessing import Pipe, Process
import os
import math
import doctable

class DistributeLoad:
    ''' Creates processing pool and gets results alongside everything else.
    '''
    def __init__(self, workers: int = None, override_maxcores: bool = True):
        '''
        Args:
            workers: number of workers in process pool.
        '''
        
        if workers is None:
            self.workers_og = os.cpu_count()
        else:
            if override_maxcores: # in case where user really wantes more workers than cores
                self.workers_og = workers
            else:
                self.workers_og = min([os.cpu_count(), workers])
        
        self.pool = None
        self.finished = True

import dataclasses
@dataclasses.dataclass
class WorkerThread:
    def __init__(self, wid: int):
        '''
        Args:
            wid: workerid of this thread.
        '''
        self.wid: int = wid
        self.pid: int = os.getpid()
    








