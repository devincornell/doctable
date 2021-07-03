import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction
from .worker import Worker
from .messaging import *

class WorkerResource:
    '''Manages a worker process and pipe to it.'''
    __slots__ = ['pipe', 'proc']
    def __init__(self, func: Callable, ind: int, *args):
        self.pipe, worker_pipe = Pipe(True)
        self.proc = Process(
            name=f'worker_{ind}', 
            target=Worker(worker_pipe, func), 
            args=args,
        )
        self.proc.start()

    ############### Pipe interface ###############
    def recv(self): return self.pipe.recv()
    def send(self): return self.pipe.send()
    def poll(self): return self.pipe.poll()
    
    ############### Process interface ###############
    def start(self):
        if self.proc.is_alive():
            raise WorkerIsDeadError('.start()', self.proc.pid)
        return self.proc.start()
    def terminate(self): 
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.terminate()', self.proc.pid)
        return self.proc.terminate()
    
    def update_userfunc(self, userfunc: Callable):
        return self.proc.send(ChangeUserFunction(userfunc))
    
    def join(self):
        if not self.proc.is_alive():
            raise ValueError('Cannot join a worker that is not alive.')
        self.proc.send(SigClose())
        return self.proc.join()
    
    def close(self):
        if not self.proc.is_alive():
            raise ValueError('Cannot close a worker that is not alive.')
        self.join()
        self.terminate()


class WorkerPool(list):

    ############### Worker Creation ###############
    def open(self, num_workers: int, func: Callable = None, *worker_args):
        if len(self) > 0:
            raise ValueError('This WorkerPool already has running workers.')
        
        # start each worker
        for ind in range(num_workers):
            self.append(WorkerResource(ind, func, *worker_args))
        return self

    ############### Low-Level Process Operations ###############
    def start(self): [w.start() for w in self]
    def join(self): [w.join() for w in self]
    def terminate(self): 
        [w.terminate() for w in self]
        self.clear()
    def close(self):
        [w.close() for w in self]
        self.clear()
    













