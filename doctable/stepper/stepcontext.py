from __future__ import annotations
import typing

from doctable.util.unit_format import format_memory
if typing.TYPE_CHECKING:
    from .stepper import Stepper

import dataclasses
import datetime
import psutil
from ..util import format_time, format_memory

from .step import Step

@dataclasses.dataclass
class StepContext:
    stepper: Stepper
    step: Step
    format_kwargs: typing.Dict[str,bool]
    
    ######################## enter/exit methods ########################
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        msg = f'END {self.step.msg}' if self.step.msg is not None else None
        self.stepper.step(message=msg, **self.format_kwargs)

    ######################## Useful Attributes ########################
    @property
    def start(self) -> datetime.datetime:
        '''Starting datetime.'''
        return self.step.ts
    
    @property
    def start_memory(self) -> int:
        '''Memory usage at the start of this step.'''
        return self.step.mem
    
    def elapsed(self) -> datetime.timedelta:
        '''Get difference between now and the starting time.'''
        return datetime.datetime.now() - self.step.ts
    
    def memory_change(self) -> int:
        '''Change in memory usage, in Bytes.'''
        return int(self.step.current_mem_bytes() - self.step.mem_bytes)
    
    ########## String Version of Properties ##########
    def start_memory_str(self) -> str:
        '''Memory usage at the start of this step.'''
        return format_memory(self.step.mem_bytes)
    
    def elapsed_str(self) -> str:
        return format_time(self.elapsed().total_seconds())
    
    def memory_change_str(self) -> str:
        return format_memory(self.memory_change())
    