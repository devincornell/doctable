import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
from .exceptions import WorkerIsDeadError, UnidentifiedMessageReceived, WorkerHasNoUserFunction


class BaseMessage:
    pass


@dataclasses.dataclass
class DataPayload(BaseMessage):
    __slots__ = ['ind', 'data', 'pid']
    ind: int
    data: Any
    pid: int# = None
    def __lt__(self, other): return self.ind < other.ind
    def __le__(self, other): return self.ind <= other.ind
    def __gt__(self, other): return self.ind > other.ind
    def __ge__(self, other): return self.ind >= other.ind
    def __eq__(self, other): return self.ind == other.ind

@dataclasses.dataclass
class ChangeUserFunction(BaseMessage):
    __slots__ = ['userfunc']
    userfunc: Callable

class SigClose(BaseMessage):
    pass


