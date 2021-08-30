import collections
import dataclasses
import gc
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List, NewType, Tuple, Union

from .exceptions import (UserFuncRaisedException, WorkerDiedError,
                         WorkerIsAliveError, WorkerIsDeadError,
                         WorkerResourceReceivedUnidentifiedMessage)
from .messaging import (BaseMessage, DataPayload, SigClose, StatusRequest,
                        UserFunc, UserFuncException, WorkerError, WorkerStatus)
from .worker import Worker


class WorkerResource:
    '''Manages a worker process and pipe to it.'''
    __slots__ = ['pipe', 'proc', 'verbose']

    def __init__(self, target: Callable = None, start: bool = False, args=None, kwargs=None, logging: bool = True, verbose: bool = False, method: str = 'forkserver'):
        '''Open Process and pipe to it.
        '''
        self.verbose = verbose

        # set up userfunc
        if target is not None:
            args = args if args is not None else tuple()
            kwargs = kwargs if kwargs is not None else dict()
            userfunc = UserFunc(target, *args, **kwargs)
        else:
            userfunc = None

        ctx = multiprocessing.get_context(method)
        self.pipe, worker_pipe = Pipe(duplex=True)
        self.proc = ctx.Process(
            target=Worker(worker_pipe, userfunc=userfunc, verbose=verbose, logging=logging), 
        )

        # start worker if requested
        if start:
            self.start()
    
    def __repr__(self):
        return f'{self.__class__.__name__}[{self.pid}]'
    
    def __enter__(self):
        if not self.is_alive():
            self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.join()
    
    def __del__(self):
        if self.verbose: print(f'{self}.__del__ was called!')
        self.terminate(check_alive=False)

    ############### Main interface methods ###############
    def poll(self) -> bool: 
        '''Check if worker sent anything.
        '''
        return self.pipe.poll()

    def execute(self, data: Any):
        '''Send data to worker and blocking return result upon reception.
        '''
        self.send_data(data)
        return self.recv_data()

    def recv_data(self) -> Any:
        '''Receive raw data from user function.'''
        return self.recv().data
    
    def send_data(self, data: Any, **kwargs) -> None:
        '''Send any data to worker process to be handled by user function.'''
        return self.send_payload(DataPayload(data, **kwargs))

    def update_userfunc(self, func: Callable, *args, **kwargs):
        '''Send a new UserFunc to worker process.
        '''
        return self.send_payload(UserFunc(func, *args, **kwargs))

    def get_status(self):
        '''Blocking request status update from worker.
        '''
        self.send_payload(StatusRequest())
        return self.recv()

    ############### Pipe interface ###############

    def send_payload(self, payload: BaseMessage) -> None:
        '''Send a Message (DataPayload or otherwise) to worker process.
        '''
        if not self.proc.is_alive():
            raise WorkerIsDeadError('.send_payload()', self.proc.pid)
        
        if self.verbose: print(f'{self} sending: {payload}')
        
        try:
            return self.pipe.send(payload)
        
        except BrokenPipeError:
            raise WorkerDiedError(self.proc.pid)

    def recv(self) -> DataPayload:
        '''Return received DataPayload or raise exception.
        '''
        try:
            payload = self.pipe.recv()
            if self.verbose: print(f'{self} received: {payload}')
        
        except (BrokenPipeError, EOFError, ConnectionResetError):
            if self.verbose: print('caught one of (BrokenPipeError, EOFError, ConnectionResetError)')
            raise WorkerDiedError(self.proc.pid)
        
        # handle incoming data
        if isinstance(payload, DataPayload) or isinstance(payload, WorkerStatus):
            return payload

        elif isinstance(payload, WorkerError):
            #self.terminate(check_alive=True)
            raise payload.e

        elif isinstance(payload, UserFuncException):
            raise UserFuncRaisedException(payload.e)
        
        else:
            raise WorkerResourceReceivedUnidentifiedMessage()
    
    ############### Process interface ###############
    @property
    def pid(self):
        '''Get process id from worker.'''
        return self.proc.pid
    
    def is_alive(self, *arsg, **kwargs):
        '''Get status of process.'''
        return self.proc.is_alive(*arsg, **kwargs)
    
    def start(self):
        '''Start the process, throws WorkerIsAliveError if already alive.'''
        if self.proc.is_alive():
            raise WorkerIsAliveError('.start()', self.proc.pid)
        return self.proc.start()
    
    def join(self, check_alive=True):
        '''Send SigClose() to Worker and then wait for it to die.'''
        if check_alive and not self.proc.is_alive():
            raise WorkerIsDeadError('.join()', self.proc.pid)
        try:
            self.pipe.send(SigClose())
        except BrokenPipeError:
            pass
        return self.proc.join()

    def terminate(self, check_alive=True): 
        '''Send terminate signal to worker.'''
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



