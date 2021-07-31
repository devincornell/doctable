import collections
import dataclasses
import gc
import multiprocessing
import os
import traceback
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, Tuple

from .exceptions import (UnidentifiedMessageReceivedError,
                         WorkerHasNoUserFunctionError, WorkerIsDeadError)
from .messaging import (DataPayload, UserFuncRaisedException, SigClose, UserFunc,
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
            except (EOFError, BrokenPipeError):
                exit(1)

            # kill worker
            if isinstance(payload, SigClose):
                exit(1)

            # process received data payload
            elif isinstance(payload, DataPayload):
                self.execute_and_send(payload)
            
            # load new function
            elif isinstance(payload, UserFunc):
                self.userfunc = payload
            
            else:
                self.send(WorkerRaisedException(UnidentifiedMessageReceivedError()))

    def execute_and_send(self, payload: DataPayload):
        '''Execute the provide function on the payload (modifies in-place), and return it.
        '''
        # check if worker has a user function
        if self.userfunc is None:
            self.send(WorkerRaisedException(WorkerHasNoUserFunctionError()))
            return
            
        # update pid and apply userfunc
        payload.pid = self.pid
        
        # try to execute function and raise any errors
        try:
            payload.data = self.userfunc.execute(payload.data)
        except BaseException as e:
            self.send(UserFuncRaisedException(e))
            #traceback.print_exc()
            return

        # send result back to WorkerResource
        self.send(payload)
        
        # garbage collect if needed
        if self.gcollect:
            gc.collect()
        

    ############## Basic Send/Receive ##############

    def recv(self):
        payload = self.pipe.recv()
        if self.verbose: print(f'{self} received: {payload}')
        return payload

    def send(self, data: Any):
        if self.verbose: print(f'{self} sending: ({type}) {data}')
        return self.pipe.send(data)

