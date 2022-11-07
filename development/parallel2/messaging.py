import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
import doctable.util
from .exceptions import WorkerHasNoUserFunctionError
import datetime

class BaseMessage:
    pass

@doctable.util.slots_dataclass(order=True)
class DataPayload(BaseMessage):
    '''For passing data to/from Workers.'''
    __slots__ = []
    data: Any = dataclasses.field(compare=False)
    ind: int = 0
    pid: int = None
    #def __lt__(self, other): return self.ind < other.ind


class StatusRequest(BaseMessage):
    pass

@doctable.util.slots_dataclass
class WorkerStatus(BaseMessage):
    __slots__ = []
    pid: int = os.getpid()
    start_ts: int = dataclasses.field(default_factory=datetime.datetime.now)
    time_waiting: int = 0
    time_working: int = 0
    jobs_finished: int = 0
    uptime: int = None # to be updated before sending

    def update_uptime(self):
        self.uptime = datetime.datetime.now() - self.start_ts

    def efficiency(self):
        return self.time_working / (self.time_working + self.time_waiting)

    def total_efficiency(self):
        return self.time_working / self.uptime.total_seconds()

    def sec_per_job(self):
        return self.time_working / self.jobs_finished

class UserFunc(BaseMessage):
    '''Contains a user function and data to be passed to it when calling.
    Sent to a process upon init and when function should be changed.
    '''
    __slots__ = ['func', 'args', 'kwargs']
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        argstr = ', '.join(self.args)
        kwargstr = ', '.join([f'{k}={v}' for k,v in self.kwargs.items()])
        return f'{self.__class__.__name__}({self.func.__name__}(x, {argstr}, {kwargstr}))'

    def execute(self, data: Any):
        '''Call function passing *args and **kwargs.
        '''
        if self.func is None:
            raise WorkerHasNoUserFunctionError()
        return self.func(data, *self.args, **self.kwargs)

class SigClose(BaseMessage):
    '''WorkerResource telling Worker to close.'''
    pass

class WorkerError(BaseMessage):
    '''Sent from Worker to WorkerResource when any worker exception is passed 
    (not userfunc).
    '''
    def __init__(self, exception):
        self.e = exception
    def __repr__(self):
        return f'{self.__class__.__name__}({self.e})'


class UserFuncException(BaseMessage):
    '''Passes exception from user function to main thread (and lets it know 
        there was an error with the user function).
    '''
    def __init__(self, exception=None):
        self.e = exception
    
    def __str__(self):
        return f'{self.__class__.__name__}({self.e.__class__.__name__})'

