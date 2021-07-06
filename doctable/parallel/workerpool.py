import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction, WorkerIsAliveError
from .worker import Worker
from .messaging import DataPayload, ChangeUserFunction, SigClose, WorkerRaisedException

class WorkerPool(list):

    ############### Worker Creation ###############
    def is_alive(self): 
        return len(self) > 0 and all([w.is_alive() for w in self])
    
    def start(self, num_workers: int, *args, func: Callable = None, **kwargs):
        if self.is_alive():
            raise ValueError('This WorkerPool already has running workers.')
        
        # start each worker
        for ind in range(num_workers):
            self.append(WorkerResource(ind, *args, func=func, **kwargs))
        
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
    def __init__(self, ind: int, *args, func: Callable = None, **kwargs):
        self.pipe, worker_pipe = Pipe(True)
        self.proc = Process(
            name=f'worker_{ind}', 
            target=Worker(worker_pipe, *args, userfunc=func, **kwargs), 
            args=args,
        )
        self.proc.start()

    ############### Pipe interface ###############
    def poll(self): return self.pipe.poll()
    def recv(self):
        msg = f'Worker {self.proc.pid} raised an exception.'

        received_data = self.pipe.recv()
        
        # raise the exception if one was passed
        if isinstance(received_data, WorkerRaisedException):
            self.join()
            print(msg)
            exit()
        
        return received_data
    def send(self, ind: int, data: Any):
        return self.pipe.send(DataPayload(ind, data, pid=self.proc.pid))
    
    ############### Process interface ###############
    @property
    def pid(self):
        return self.proc.pid
    def is_alive(self, *arsg, **kwargs):
        return self.proc.is_alive(*arsg, **kwargs)
    
    def start(self):
        if self.proc.is_alive():
            raise WorkerIsAliveError('.start()', self.proc.pid)
        return self.proc.start()
    
    def update_userfunc(self, userfunc: Callable):
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.update_userfunc()', self.proc.pid)
        return self.pipe.send(ChangeUserFunction(userfunc))
    
    def join(self):
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.join()', self.proc.pid)
        try:
            self.pipe.send(SigClose())
        except BrokenPipeError:
            pass
        return self.proc.join()

    def terminate(self): 
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.terminate()', self.proc.pid)
        return self.proc.terminate()

    





