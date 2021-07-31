import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
import doctable.util

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

class UserFunc(BaseMessage):
    '''Contains a user function and data to be passed to it when calling.
    Sent to a process upon init and when function should be changed.
    '''
    __slots__ = ['func', 'args', 'kwargs']
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    @property
    def is_valid(self):
        return self.func is not None

    def execute(self, data: Any):
        '''Call function passing *args and **kwargs.
        '''
        return self.func(data, *self.args, **self.kwargs)

class SigClose(BaseMessage):
    '''WorkerResource telling Worker to close.'''
    pass

class WorkerErrorMessage(BaseMessage):
    '''Sent from Worker to WorkerResource when there is a problem (must provide the exception to raise).
    '''
    def __init__(self, exception):
        self.e = exception


class WorkerRaisedException(BaseMessage):
    '''Sent from Worker to WorkerResource when worker encountered exception.'''
    def __init__(self, exception=None):
        self.e = exception

