import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction

@dataclasses.dataclass
class DataPayload:
    __slots__ = ['ind', 'data', 'pid']
    ind: int
    data: Any
    pid: int

@dataclasses.dataclass
class ChangeUserFunction:
    __slots__ = ['userfunc']
    userfunc: Callable

class SigClose:
    pass



@dataclasses.dataclass
class Worker:
    '''Basic worker meant to be run in a process.'''
    pipe: multiprocessing.Pipe
    userfunc: Callable = None
    gcollect: bool = False
    def __call__(self, *args, payloads: Iterable[DataPayload] = None, **kwargs):
        '''Call when opening the process.
        '''
        self.pid = os.getpid()

        # process payloads provided at init
        if payloads is not None:
            self.execute_userfunc(payloads, args, kwargs)
        
        # process received data
        while True:
            payload = self.pipe.recv()

            # process received data payload
            if isinstance(payload, DataPayload):
                payload = self.execute_userfunc([payload], args, kwargs)
                self.pipe.send(payload)
            
            # load new function
            elif isinstance(payload, ChangeUserFunction):
                self.userfunc = payload.userfunc
            
            # kill worker
            elif isinstance(payload, SigClose):
                exit(0)
            
            else:
                raise UnidentifiedMessageReceived(self.pid)

    def execute_userfunc(self, payloads: Iterable[DataPayload], args, kwargs):
        '''Execute the provide function on the payload (modifies in-place).
        ''' 
        # check if worker has a user function
        if self.userfunc is None:
            raise WorkerHasNoUserFunction(self.pid)

        # process each provided payload
        for payload in payloads:
            payload.pid = self.pid
            payload.data = self.userfunc(payload.data, *args, **kwargs)
            if self.gcollect:
                gc.collect()
        return payload
            




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
    













