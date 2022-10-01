from __future__ import annotations
import dataclasses
import datetime
import psutil
import os

from doctable.util.unit_format import format_memory
from ..util import format_memory, format_time

@dataclasses.dataclass
class Step:
    i: int
    msg: str
    ts: datetime
    pid: int
    mem: psutil.pmem = None
    
    def __post_init__(self):
        self.mem = self.current_mem()

    @classmethod
    def now(cls, i: int = None, msg: str = None, pid: int = None) -> Step:
        '''Create a new step based on current timestamp/memory usage.'''
        pid = pid if pid is not None else os.getpid()
        return cls(
            i = i,
            msg = msg,
            ts = datetime.datetime.now(),
            pid = pid,
            #mem = psutil.Process(pid).memory_info(),#psutil.virtual_memory(),
        )

    def current_mem(self) -> psutil.pmem:
        '''Get current memory usage.'''
        return psutil.Process(self.pid).memory_info()
    
    def current_mem_bytes(self) -> int:
        return self.current_mem().rss
    
    def __sub__(self, other: Step):
        return self.ts_diff(other)

    def ts_diff(self, other: Step):
        return (self.ts - other.ts).total_seconds()
    
    @property
    def mem_bytes(self) -> int:
        '''Get memory usage in bytes.'''
        return self.mem.rss

    def format(self, prev_step: Step = None, show_ts=True, show_delta=True, show_mem=True):
        if show_ts:
            ts_str = f"{self.ts.strftime('%a %H:%M:%S')}/"
        else:
            ts_str = ''

        if show_mem:
            mem_usage = f"{format_memory(self.mem_bytes):>9}/"
        else:
            mem_usage = ''

        if show_delta:
            if prev_step is not None:
                ts_diff = f"+{format_time(self.ts_diff(prev_step)):>10}/"
            else:
                ts_diff = f'{" "*11}/'
        else:
            ts_diff = ''

        return f'{ts_str}{mem_usage}{ts_diff}{self.i:2}: {self.msg}'
        
        