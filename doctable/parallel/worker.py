import collections
import dataclasses
import gc
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, Tuple

from .exceptions import (UnidentifiedMessageReceivedError,
                         WorkerHasNoUserFunctionError, WorkerIsDeadError)
from .messaging import (DataPayload, WorkerErrorMessage, SigClose, UserFunc,
                        WorkerRaisedException)


@dataclasses.dataclass
class Worker:
    '''Basic worker meant to be run in a process.'''
    pipe: multiprocessing.Pipe
    userfunc: UserFunc = None
    gcollect: bool = False
    verbose: bool = False

    @property
    def pid(self):
        return os.getpid()

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.pid}]'

    def __call__(self):
        '''Call when opening the process.
        '''
        
        # main receive/send loop
        while True:

            # wait to receive data
            try:
                payload = self.recv()
            except EOFError:
                # parent process died
                break

            # process received data payload
            if isinstance(payload, DataPayload):
                payload = self.execute_userfunc(payload)
                self.send(payload)
            
            # load new function
            elif isinstance(payload, UserFunc):
                self.userfunc = payload
            
            # kill worker
            elif isinstance(payload, SigClose):
                exit(0)
            
            else:
                self.pipe.send(WorkerErrorMessage(UnidentifiedMessageReceivedError()))

    def recv(self):
        payload = self.pipe.recv()
        if self.verbose: print(f'{self} received: {payload}')
        return payload

    def send(self, data: Any):
        if self.verbose: print(f'{self} sending: {data}')
        return self.pipe.send(data)

    def execute_userfunc(self, payload: DataPayload):
        '''Execute the provide function on the payload (modifies in-place), and return it.
        '''
        # check if worker has a user function
        if self.userfunc.is_valid:
            
            # update pid and apply userfunc
            payload.pid = self.pid
            
            # try to execute function and raise any errors
            try:
                payload.data = self.userfunc.execute(payload.data)
            except BaseException as e:
                self.pipe.send(WorkerRaisedException(e))
                raise e
            
            # garbage collect if needed
            if self.gcollect:
                gc.collect()
            
            return payload
        
        else:
            self.pipe.send(WorkerErrorMessage(WorkerHasNoUserFunctionError()))
