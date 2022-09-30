
from __future__ import annotations

import typing
import datetime
import psutil
import os
import dataclasses

import doctable



@dataclasses.dataclass
class Step:
    i: int
    msg: str
    ts: datetime# = field(default_factory=datetime.now)
    mem: int#psutil._pslinux.svmem# = field(default_factory=lambda: psutil.virtual_memory().used)

    @classmethod
    def now(cls, i: int = None, msg: str = None, pid: int = None) -> Step:
        '''Create a new step based on current timestamp/memory usage.'''
        pid = pid if pid is not None else os.getpid()
        return cls(
            i = i,
            msg = msg,
            ts = datetime.datetime.now(),
            mem = psutil.Process(pid).memory_info()#psutil.virtual_memory(),
        )


    #################################### For Getting up-to-date info ####################################
    @property
    def mem_used(self) -> int:
        '''Memory usage at the start of this step.'''
        return self.mem.vms
    
    #################################### For Printing ####################################
    def __sub__(self, other: Step):
        return self.ts_diff(other)

    def ts_diff(self, other: Step):
        return (self.ts - other.ts).total_seconds()

    def format(self, prev_step: Step = None, name: str = None, show_ts=True, show_delta=True, show_mem=True):
        if show_ts:
            ts_str = f"{self.ts.strftime('%a %H:%M:%S')}/"
        else:
            ts_str = ''

        if show_mem:
            mem_usage = f"{doctable.format_memory(self.mem_used):>9}/"
        else:
            mem_usage = ''

        if show_delta:
            if prev_step is not None:
                ts_diff = f"+{doctable.format_time(self.ts_diff(prev_step)):>10}/"
            else:
                ts_diff = f'{" "*11}/'
        else:
            ts_diff = ''
            
        if name is not None:
            name_str = f'{name} | '
        else:
            name_str = ''

        return f'{name_str}{ts_str}{mem_usage}{ts_diff}{self.i:2}: {self.msg}'

