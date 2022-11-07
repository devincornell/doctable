import collections
import dataclasses
import gc
import multiprocessing
import os
import traceback
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, Tuple

from .exceptions import (UnidentifiedMessageReceivedError)
from .messaging import BaseMessage, MessageType, WorkerError, UserFuncException, DataPayload
from .workerstatus import WorkerStatus, WorkerStatusDummy

import time

@dataclasses.dataclass
class WorkerProcess:
    '''Basic worker meant to be run in a process.'''
    pipe: multiprocessing.Pipe
    gcollect: bool = False
    verbose: bool = False
    logging: bool = False
    status: WorkerStatus = None
    
    def __post_init__(self):
        '''Make a new status object.
        '''
        if self.logging:
            self.status = WorkerStatus()
        else:
            self.status = WorkerStatusDummy()
        

    @property
    def pid(self):
        return os.getpid()

    def __repr__(self):
        return f'{self.__class__.__name__}[{self.pid}]'

    def __call__(self, userfunc: Callable):
        '''Start the process.
        '''
        self.print(f'process started!: {userfunc}')
        
        # main receive/send loop
        while True:
            # wait to receive data
            try:
                with self.status.waiting():
                    message = self.recv()
            except (EOFError, BrokenPipeError):
                # don't send anything back because host is not available
                exit(1)
            
            # kill worker
            if message.type is MessageType.CLOSE:
                exit(0)

            # process received data payload
            elif message.type is MessageType.DATA:
                self.execute_and_send(userfunc, message)

            # return status of worker
            elif message.type is MessageType.STATUS_REQUEST:
                self.status.update()
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
            with self.status.working():
                payload.data = userfunc(payload.data)
        
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
        self.print(f'waiting to receive')
        message = self.pipe.recv()
        self.print(f'received {message.type}')
        return message

    def send(self, message: BaseMessage):
        self.print(f'sending {message.type}')
        return self.pipe.send(message)

    def print(self, message):
        if self.verbose:
            print(f'{self}: {message}')

