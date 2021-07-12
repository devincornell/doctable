import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, Tuple, NewType
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction, WorkerIsAliveError, WorkerDiedError
from .worker import Worker, UserFuncArgs
from .messaging import DataPayload, ChangeUserFunction, SigClose, WorkerRaisedException


class WorkerResource:
    '''Manages a worker process and pipe to it.'''
    __slots__ = ['pipe', 'proc', 'verbose']
    verbose = False

    def __init__(self, ind: int = 0, userfunc: Callable = None, datas: Iterable[Any] = None, userfunc_args: UserFuncArgs = None, start: bool = True):
        '''Open Process and pipe to it.
        '''
        if datas is None:
            datas = list()

        if userfunc_args is None:
            userfunc_args = UserFuncArgs()

        self.pipe, worker_pipe = Pipe(True)
        self.proc = Process(
            name=f'worker_{ind}', 
            target=Worker(worker_pipe, userfunc=userfunc), 
            args=[datas, userfunc_args], 
        )

        # start worker if requested
        if start:
            self.proc.start()

    ############### Pipe interface ###############
    def poll(self): 
        '''Check if worker sent anything.
        '''
        return self.pipe.poll()
    
    def recv(self):
        '''Receive and handle received message.
        '''
        try:
            payload = self.pipe.recv()
            if self.verbose: print(f'WorkerResource({self.pid}) received: {payload}')
        except BrokenPipeError:
            if self.verbose: print('caught BrokenPipeError')
            raise WorkerDiedError(self.proc.pid)
        
        # raise the exception if one was passed
        if isinstance(payload, WorkerRaisedException):
            raise WorkerDiedError(self.proc.pid)
        
        return payload
    
    def send_payload(self, payload: DataPayload):
        '''Send a DataPayload to worker process.
        '''
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.send_payload()', self.proc.pid)
        
        payload.pid = self.proc.pid
        try:
            if self.verbose: print(f'WorkerResource({self.pid}) sending: {payload}')
            return self.pipe.send(payload)
        except BrokenPipeError:
            raise WorkerDiedError(self.proc.pid)

    def update_userfunc(self, userfunc: Callable):
        '''Send a new UserFunc to worker process.
        '''
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.update_userfunc()', self.proc.pid)
        try:
            if self.verbose: print(f'WorkerResource({self.pid}) changing userfunc: {userfunc}')
            return self.pipe.send(ChangeUserFunction(userfunc))
        except BrokenPipeError:
            raise WorkerDiedError(self.proc.pid)
    
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



