import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction, WorkerIsAliveError
from .worker import Worker
from .messaging import DataPayload, ChangeUserFunction, SigClose

class WorkerPool(list):

    ############### Worker Creation ###############
    def is_alive(self): 
        return len(self) > 0 and all([w.is_alive() for w in self])
    def start(self, num_workers: int, func: Callable = None, *worker_args):
        if self.is_alive():
            raise ValueError('This WorkerPool already has running workers.')
        
        # start each worker
        for ind in range(num_workers):
            self.append(WorkerResource(ind, func, *worker_args))
        
        return self

    def update_userfunc(self, userfunc: Callable):
        return [w.update_userfunc(userfunc) for w in self]

    ############### Low-Level Process Operations ###############
    def join(self):
        [w.join() for w in self]
        self.clear()
    def terminate(self): 
        [w.terminate() for w in self]
        self.clear()


class WorkerResource:
    '''Manages a worker process and pipe to it.'''
    __slots__ = ['pipe', 'proc']
    def __init__(self, ind: int, func: Callable = None, *args):
        self.pipe, worker_pipe = Pipe(True)
        self.proc = Process(
            name=f'worker_{ind}', 
            target=Worker(worker_pipe, func), 
            args=args,
        )
        self.proc.start()

    ############### Pipe interface ###############
    def poll(self): return self.pipe.poll()
    def recv(self): return self.pipe.recv()
    def send(self, ind: int, data: Any):
        return self.pipe.send(DataPayload(ind, data, pid=self.proc.pid))
    
    ############### Process interface ###############
    @property
    def pid(self):
        return self.proc.pid
    def is_alive(self, *arsg, **kwargs):
        return self.proc.is_alive(*arsg, **kwargs)
    
    def start(self):
        print(f'{self.proc.is_alive()}')
        if self.proc.is_alive():
            raise WorkerIsAliveError('.start()', self.proc.pid)
        return self.proc.start()
    
    def update_userfunc(self, userfunc: Callable):
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.update_userfunc()', self.proc.pid)
        return self.proc.send(ChangeUserFunction(userfunc))
    
    def join(self):
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.join()', self.proc.pid)
        self.pipe.send(SigClose())
        return self.proc.join()

    def terminate(self): 
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.terminate()', self.proc.pid)
        return self.proc.terminate()

    





