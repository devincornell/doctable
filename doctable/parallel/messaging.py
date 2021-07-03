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
    #__slots__ = ['ind', 'data', 'pid']
    ind: int
    data: Any
    pid: int = None

@dataclasses.dataclass
class ChangeUserFunction(BaseMessage):
    __slots__ = ['userfunc']
    userfunc: Callable

class SigClose(BaseMessage):
    pass


