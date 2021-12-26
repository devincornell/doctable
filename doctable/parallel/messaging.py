import collections
import dataclasses
import multiprocessing
import os
from multiprocessing import Lock, Pipe, Pool, Process, Value
from typing import Any, Callable, Dict, Iterable, List
import gc
import doctable.util
from .exceptions import UnidentifiedMessageReceivedError
import datetime

import enum

class MessageType(enum.Enum):
    DATA = 1
    STATUS_REQUEST = 2
    STATUS = 3
    CLOSE = 4
    ERROR = 5
    USERFUNC_EXCEPTION = 6

class BaseMessage:
    '''All messages between WorkerProcess and WorkerResource inherit from this.
    '''
    __slots__ = []
    message_type: MessageType = None
    
    @property
    def type(self):
        '''To be accessed 
        '''
        if self.message_type is None:
            raise UnidentifiedMessageReceivedError()
        return self.message_type

@doctable.util.slots_dataclass(order=True)
class DataPayload(BaseMessage):
    '''Data is passed to/from WorkerResource and WorkerProcess.
    '''
    __slots__ = []
    message_type = MessageType.DATA

    data: Any = dataclasses.field(compare=False)
    ind: int = 0
    pid: int = None

class StatusRequest(BaseMessage):
    '''WorkerResource requests status from WorkerProcess.
    '''
    __slots__ = []
    message_type = MessageType.STATUS_REQUEST

@doctable.util.slots_dataclass
class SigClose(BaseMessage):
    '''WorkerResource tells WorkerProcess to close.
    '''
    __slots__ = []
    message_type = MessageType.CLOSE

@doctable.util.slots_dataclass
class WorkerError(BaseMessage):
    '''WorkerProcess tells WorkerResource that it encountered an exception.
    '''
    __slots__ = []
    message_type = MessageType.ERROR
    
    def __init__(self, exception):
        self.e = exception
    
    def __repr__(self):
        return f'{self.__class__.__name__}({self.e})'


@doctable.util.slots_dataclass
class UserFuncException(BaseMessage):
    '''WorkerProcess tells WorkerResource that the UserFunc encountered an exception.
    '''
    __slots__ = []
    message_type = MessageType.USERFUNC_EXCEPTION

    def __init__(self, exception=None):
        self.e = exception
    
    def __str__(self):
        return f'{self.__class__.__name__}({self.e.__class__.__name__})'

