from __future__ import annotations
import dataclasses
import datetime
import psutil
import os



@dataclasses.dataclass
class Step:
    i: int
    msg: str
    ts: datetime.datetime
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

        
        