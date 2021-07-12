import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction
import doctable.util

class BaseMessage:
    pass

@doctable.util.slots_dataclass
class DataPayload(BaseMessage):
    __slots__ = []    
    data: Any
    ind: int = 0
    pid: int = None
    def __lt__(self, other): return self.ind < other.ind
    #def __le__(self, other): return self.ind <= other.ind
    #def __gt__(self, other): return self.ind > other.ind
    #def __ge__(self, other): return self.ind >= other.ind
    #def __eq__(self, other): return self.ind == other.ind

@dataclasses.dataclass
class ChangeUserFunction(BaseMessage):
    __slots__ = ['userfunc']
    userfunc: Callable

class SigClose(BaseMessage):
    '''Sent from main to worker when worker needs to be closed.'''
    pass

class WorkerRaisedException(BaseMessage):
    '''Sent from worker to main when worker encountered exception.'''
    pass


