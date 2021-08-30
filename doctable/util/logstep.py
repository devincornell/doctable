
import doctable
import datetime
import dataclasses
import psutil
from .slots import slots_dataclass
from typing import Callable, List, Dict, Any, TypeVar

LogStepType = TypeVar('LogStepType')

@slots_dataclass
class LogStepDiff:
    __slots__ = []
    ind_diff: int
    ts_diff: datetime.timedelta
    mem_diff: int
    msg1: str
    msg2: str
    meta1: Any
    meta2: Any

@slots_dataclass
class LogStep:
    __slots__ = []
    ind: int = None
    msg: str = None
    ts: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)
    mem: int = dataclasses.field(default_factory=lambda: psutil.virtual_memory().used)
    meta: Any = None

    def diff(self, other: LogStepType) -> LogStepDiff:
        return LogStepDiff(
            ind_diff = self.ind - other.ind,
            ts_diff = self.ts - other.ts,
            mem_diff = self.mem - other.mem,
            msg1 = self.msg,
            msg2 = other.msg,
            meta1 = self.meta,
            meta2 = other.meta,
        )

    def __sub__(self, other: LogStepType):
        '''See .diff().'''
        return self.diff(other)

