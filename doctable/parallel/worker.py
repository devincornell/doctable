import collections
import dataclasses
import gc
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List

from .exceptions import (UnidentifiedMessageReceived, WorkerHasNoUserFunction,
                         WorkerIsDeadError)
from .messaging import DataPayload, SigClose, ChangeUserFunction

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
            
