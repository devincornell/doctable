import collections
import dataclasses
import gc
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, NewType, Tuple, Union

from .exceptions import (WorkerDiedError,
                         WorkerIsAliveError,
                         WorkerIsDeadError, WorkerResourceReceivedUnidentifiedMessage)
from .messaging import DataPayload, SigClose, UserFunc, WorkerRaisedException, WorkerErrorMessage
from .worker import Worker


class WorkerResource:
    '''Manages a worker process and pipe to it.'''
    __slots__ = ['pipe', 'proc']
    verbose = False

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.pid}]'

    def __init__(self, target: Callable = None, start: bool = True, args=None, kwargs=None):
        '''Open Process and pipe to it.
        '''
        # set up userfunc
        args = args if args is not None else tuple()
        kwargs = kwargs if kwargs is not None else dict()
        userfunc = UserFunc(target, *args, **kwargs)

        self.pipe, worker_pipe = Pipe(True)
        self.proc = Process(
            target=Worker(worker_pipe, userfunc=userfunc), 
        )

        # start worker if requested
        if start:
            self.start()
    
    def __del__(self):
        self.terminate(check_alive=False)

    ############### Pipe interface ###############
    def poll(self): 
        '''Check if worker sent anything.
        '''
        return self.pipe.poll()

    def recv_data(self):
        '''Receive raw data.'''
        return self.recv().data
    
    def send_data(self, data: Any):
        '''Send any data to worker process.'''
        return self.send_payload(DataPayload(data))
    
    def recv(self) -> DataPayload:
        '''Receive and handle received message.
        '''
        try:
            payload = self.pipe.recv()
            if self.verbose: print(f'{self} received: {payload}')
        
        except BrokenPipeError:
            if self.verbose: print('caught BrokenPipeError')
            raise WorkerDiedError(self.proc.pid)

        except EOFError:
            if self.verbose: print('caught EOFError')
            raise WorkerDiedError(self.proc.pid)
        
        # handle incoming data
        if isinstance(payload, DataPayload):
            return payload

        elif isinstance(payload, WorkerRaisedException):
            self.join()
            raise WorkerDiedError(self.proc.pid)

        elif isinstance(payload, WorkerErrorMessage):
            self.join()
            raise payload.e
        
        else:
            raise WorkerResourceReceivedUnidentifiedMessage()

    def send_payload(self, payload: DataPayload):
        '''Send a DataPayload to worker process.
        '''
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.send_payload()', self.proc.pid)
        
        payload.pid = self.proc.pid
        try:
            if self.verbose: print(f'{self} sending: {payload}')
            return self.pipe.send(payload)
        
        except BrokenPipeError:
            raise WorkerDiedError(self.proc.pid)

    def update_userfunc(self, func: Callable, *args, **kwargs):
        '''Send a new UserFunc to worker process.
        '''
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.update_userfunc()', self.proc.pid)
        try:
            if self.verbose: print(f'{self} changing userfunc: {func}')
            return self.pipe.send(UserFunc(func, *args, **kwargs))
        except BrokenPipeError:
            raise WorkerDiedError(self.proc.pid)

    def execute(self, data: Any):
        '''Blocking send data to worker and return result upon reception.
        '''
        self.send_data(data)
        return self.recv_data()


    
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
    
    def join(self, check_alive=True):
        if check_alive and not self.proc.is_alive():
            raise WorkerIsDeadError('.join()', self.proc.pid)
        try:
            self.pipe.send(SigClose())
        except BrokenPipeError:
            pass
        return self.proc.join()

    def terminate(self, check_alive=True): 
        if check_alive and not self.proc.is_alive():
            raise WorkerIsDeadError('.terminate()', self.proc.pid)
        return self.proc.terminate()

#class WorkerPool(list):
#
#    ############### Worker Creation ###############
#    def is_alive(self): 
#        return len(self) > 0 and all([w.is_alive() for w in self])
#    
#    def start(self, num_workers: int, *args, func: Callable = None, **kwargs):
#        if self.is_alive():
#            raise ValueError('This WorkerPool already has running workers.')
#        
#        # start each worker
#        for ind in range(num_workers):
#            self.append(WorkerResource(ind, *args, func=func, **kwargs))
#        
#        return self
#
#    def update_userfunc(self, userfunc: Callable):
#        return [w.update_userfunc(userfunc) for w in self]
#
#    ############### Low-Level Process Operations ###############
#    def join(self):
#        [w.join() for w in self]
#        self.clear()
#    
#    def terminate(self): 
#        [w.terminate() for w in self]
#        self.clear()



