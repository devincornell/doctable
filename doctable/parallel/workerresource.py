from __future__ import annotations
import functools
import typing
import dataclasses
import multiprocessing
import multiprocessing.connection
#from multiprocessing import Lock, Pipe, Pool, Process, Value
#from typing import Any, Callable, Dict, Iterable, List, NewType, Tuple, Union

from .exceptions import (UserFuncRaisedException, WorkerDiedError,
                         WorkerIsAliveError, WorkerIsDeadError,
                         WorkerResourceReceivedUnidentifiedMessage)
from .messaging import (BaseMessage, DataPayload, SigClose, StatusRequest)
#from .userfunc import UserFunc
from .workerprocess import WorkerProcess
from .messaging import MessageType



@dataclasses.dataclass
class WorkerResource:
    '''Manages a worker process and pipe to it.
    '''
    method: str = None
    logging: bool = True
    verbose: bool = False
    proc: multiprocessing.Process = None
    pipe: multiprocessing.connection.Connection = None
        
    def __enter__(self):
    #    #if not self.is_alive():
    #    #    self.start()
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        if self.is_alive():
            self.join()
    
    def __del__(self):
        self.print(f'__del__ was called!')
        try:
            self.terminate(check_alive=False)
        except:
            pass

    ############### Main interface methods ###############
    def poll(self) -> bool: 
        '''Check if worker sent anything.
        '''
        if not self.is_alive():
            raise WorkerIsDeadError('.poll()', self.proc.pid)
        return self.pipe.poll()

    def execute(self, data: typing.Any) -> typing.Any:
        '''Send data to worker and blocking return result upon reception.
        '''
        self.send_data(data)
        return self.recv_data()

    def recv_data(self) -> typing.Any:
        '''Receive raw data from user function.'''
        return self.recv().data
    
    def send_data(self, data: typing.Any, **kwargs) -> None:
        '''Send any data to worker process to be handled by user function.'''
        return self.send_message(DataPayload(data, **kwargs))

    def get_status(self) -> typing.Any:
        '''Blocking request status update from worker.
        '''
        self.send_message(StatusRequest())
        return self.recv()

    ############### Pipe interface ###############

    def send_message(self, message: BaseMessage) -> None:
        '''Send a Message (DataPayload or otherwise) to worker process.
        '''
        if not self.is_alive():
            raise WorkerIsDeadError('.send_message()', self.proc.pid)
        
        self.print(f'sending: {message.type}')
        
        try:
            return self.pipe.send(message)
        
        except BrokenPipeError:
            raise WorkerDiedError(self.proc.pid)

    def recv(self) -> DataPayload:
        '''Return received DataPayload or raise exception.
        '''
        try:
            message = self.pipe.recv()
            self.print(f'received: {message.type}')
        
        except (BrokenPipeError, EOFError, ConnectionResetError):
            self.print('caught one of (BrokenPipeError, EOFError, ConnectionResetError)')
            raise WorkerDiedError(self.proc.pid)
        
        # handle incoming data
        if message.type in (MessageType.DATA, MessageType.STATUS):
            return message

        elif message.type is MessageType.ERROR:
            #self.terminate(check_alive=True)
            raise message.e

        elif message.type is MessageType.USERFUNC_EXCEPTION:
            raise UserFuncRaisedException(message.e)
        
        else:
            raise WorkerResourceReceivedUnidentifiedMessage()
    
    ############### Process interface ###############
    def is_alive(self) -> bool:
        '''Get status of process.
        '''
        return self.proc is not None and self.proc.is_alive()

    def start(self, userfunc: typing.Callable, *userfunc_args, **userfunc_kwargs) -> WorkerResource:
        '''Create a new WorkerProcess and start it. Can be used in context manager.
        '''
        self.print('starting process')

        ctx = multiprocessing.get_context(self.method)
        self.pipe, worker_pipe = ctx.Pipe(duplex=True)
        target = WorkerProcess(worker_pipe, verbose=self.verbose, logging=self.logging)

        self.proc = ctx.Process(
            target=target, 
            args=(functools.partial(userfunc, *userfunc_args, **userfunc_kwargs),)
        )
        
        self.proc.start()
        
        return self
    
    def join(self, check_alive=True) -> None:
        '''Send SigClose() to Worker and then wait for it to die.'''
        if check_alive and not self.is_alive():
            raise WorkerIsDeadError('.join()', self.proc.pid)
        try:
            self.pipe.send(SigClose())
        except BrokenPipeError:
            pass
        return self.proc.join()

    def terminate(self, check_alive=True) -> None: 
        '''Send terminate signal to worker.'''
        if check_alive and not self.is_alive():
            raise WorkerIsDeadError('.terminate()', self.proc.pid)
        return self.proc.terminate()


    ############### Printing and debugging ###############

    @property
    def pid(self) -> int:
        '''Get process id from worker.
        '''
        return self.proc.pid

    def print(self, message: str) -> None:
        if self.verbose:
            try:
                print(f'{self.__class__.__name__}[{self.pid}]: {message}')
            except AttributeError:
                print(f'{self.__class__.__name__}[]: {message}')
            

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



