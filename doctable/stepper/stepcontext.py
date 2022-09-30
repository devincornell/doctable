from __future__ import annotations
import dataclasses
import datetime
import psutil
from .step import Step

@dataclasses.dataclass
class StepContext:
    stepper: "Stepper"
    step: Step
    
    ######################## enter/exit methods ########################
    def __enter__(self):
        #self.context_stack.append(self.last)
        #return self
        pass
        
    def __exit__(self, *args):
        #start = self.context_stack.pop()
        #end = self.step(f'END {start.msg}')
        self.stepper()

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
        return psutil.virtual_memory().used - self.step.mem