import collections
import dataclasses
import gc
import multiprocessing
import os
import traceback
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, Tuple

from .exceptions import (UnidentifiedMessageReceivedError)
from .messaging import MessageType, WorkerError, UserFuncException, DataPayload
from .workerstatus import WorkerStatus

import time

@dataclasses.dataclass
class WorkerProcess:
    '''Basic worker meant to be run in a process.'''
    pipe: multiprocessing.Pipe
    gcollect: bool = False
    verbose: bool = False
    logging: bool = False
    status: WorkerStatus = dataclasses.field(default_factory=WorkerStatus)

    @property
    def pid(self):
        return os.getpid()

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.pid}]'

    def __call__(self, userfunc: Callable):
        '''Call when opening the process.
        '''
        
        # main receive/send loop
        while True:

            # wait to receive data
            try:
                if self.logging: start = time.time()
                message = self.recv()
                if self.logging: self.status.time_waiting += time.time() - start
            except (EOFError, BrokenPipeError):
                exit(1)

            # kill worker
            if message.type is MessageType.CLOSE:
                exit(1)

            # process received data payload
            elif message.type is MessageType.DATA:
                self.execute_and_send(message)

            # return status of worker
            elif message.type is MessageType.STATUS_REQUEST:
                self.status.update_uptime()
                self.send(self.status)
            
            else:
                self.send(WorkerError(UnidentifiedMessageReceivedError()))

    def execute_and_send(self, userfunc: Callable, payload: DataPayload):
        '''Execute the provide function on the payload (modifies in-place), and return it.
        '''
        # update pid and apply userfunc to datapayload
        payload.pid = self.pid
        
        # try to execute function and raise any errors
        try:
            if self.logging: start = time.time()
            payload.data = userfunc(payload.data)
            if self.logging:
                self.status.time_working += time.time() - start
                self.status.jobs_finished += 1
        
        except BaseException as e:
            self.send(UserFuncException(e))
            traceback.print_exc()
            return

        # send result back to WorkerResource
        self.send(payload)
        
        # garbage collect if needed
        if self.gcollect:
            gc.collect()
        

    ############## Basic Send/Receive ##############

    def recv(self):
        if self.verbose: print(f'{self} waiting to receive')
        payload = self.pipe.recv()
        if self.verbose: print(f'{self} received: {payload}')
        return payload

    def send(self, data: Any):
        if self.verbose: print(f'{self} sending: {data}')
        return self.pipe.send(data)

