import collections
import dataclasses
import gc
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, Tuple

from .exceptions import (UnidentifiedMessageReceived, WorkerHasNoUserFunction,
                         WorkerIsDeadError)
from .messaging import DataPayload, SigClose, ChangeUserFunction, WorkerRaisedException


class UserFuncArgs:
    __slots__ = ['args', 'kwargs']
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

@dataclasses.dataclass
class Worker:
    '''Basic worker meant to be run in a process.'''
    pipe: multiprocessing.Pipe
    userfunc: Callable = None
    gcollect: bool = False
    verbose: bool = False

    @property
    def pid(self):
        return os.getpid()

    def __call__(self, userfunc_args: UserFuncArgs):
        '''Call when opening the process.
        Args:
            userfunc_args: args to be passed to current userfunc on every execution.
        '''
        
        # main receive/send loop
        while True:
            try:
                payload = self.recv()
            except EOFError:
                # parent process died
                break

            # process received data payload
            if isinstance(payload, DataPayload):
                payload = self.execute_userfunc(payload, userfunc_args)
                self.send(payload)
            
            # load new function
            elif isinstance(payload, ChangeUserFunction):
                self.userfunc = payload.userfunc
            
            # kill worker
            elif isinstance(payload, SigClose):
                exit(0)
            
            else:
                raise UnidentifiedMessageReceived(self.pid)

    def recv(self):
        payload = self.pipe.recv()
        if self.verbose: print(f'Worker({self.pid}) received: {payload}')
        return payload

    def send(self, data: Any):
        if self.verbose: print(f'Worker({self.pid}) sending: {data}')
        return self.pipe.send(data)

    def execute_userfunc(self, payload: DataPayload, userfunc_args: UserFuncArgs):
        '''Execute the provide function on the payload (modifies in-place), and return it.
        '''
        # check if worker has a user function
        if self.userfunc is None:
            raise WorkerHasNoUserFunction(self.pid)

        # update pid and apply userfunc
        payload.pid = self.pid
        
        try:
            payload.data = self.userfunc(payload.data, *userfunc_args.args, **userfunc_args.kwargs)
        except BaseException as e:
            self.pipe.send(WorkerRaisedException())
            raise e
        
        # garbage collect if needed
        if self.gcollect:
            gc.collect()
        
        return payload
            
