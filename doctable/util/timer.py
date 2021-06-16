
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, TypeVar
import os
import psutil
import pathlib
import collections

import doctable

StepType = TypeVar('StepType')

class Timer:
    """ Times a task.
    """
    def __init__(self, message: str = None, logfile=None, new_log=False, verbose=True):
        ''' Add single step for current datetime.
        '''
        self.verbose = verbose
        self.logfile = pathlib.Path(logfile) if logfile is not None else None
        self.steps = list()
        self.enterstack = collections.deque()
        
        # create a new logfile if needed
        if new_log and self.logfile is not None:
            self.rm_log()
            self.write_log(f"{'='*10} New Timer {'='*10}")

        # add first timestamp (don't print star)
        self.step(message=message, verbose=message is not None)

    ######################## basic accessors ########################
    def __len__(self):
        return len(self.steps)
    
    def __getitem__(self, ind):
        return self.steps[ind]
    
    @property
    def last(self):
        return self[-1] if len(self.steps) else None

    @property
    def first(self):
        return self[0] if len(self.steps) else None

    ######################## enter/exit methods ########################
    def __enter__(self):
        self.enterstack.append(self.last)
        return self
        
    def __exit__(self, *args):
        start = self.enterstack.pop()
        end = self.step(f'END {start.msg}')
    
    ######################## main functionality ########################
    def step(self, message=None, verbose=None, **format_args):
        ''' Add a new step, print and log it if needed.
        '''
        # create new step
        newstep = Step(message, len(self.steps))
        #print(f'making step: {newstep}')
        self.print_step(newstep)

        # add step
        self.steps.append(newstep)
        return newstep
    
    ######################## logging functionality ########################
    def print_step(self, step: StepType, verbose=None, **format_args):
        if len(self):
            out_str = step.format(self.steps[step.i-1], **format_args)
        else:
            out_str = step.format(**format_args)
        
        # write to log if enabled
        if self.logfile is not None:
            self.write_log(out_str)
        
        # print to output if requested
        if verbose or (verbose is None and self.verbose):
            print(out_str)

    def write_log(self, text: str):
        ''' Write text to log file.
        '''
        # create new log file if does not exist
        if not self.logfile.exists():
            self.logfile.parents[0].mkdir(parents=True, exist_ok=True)
            with self.logfile.open('w') as f:
                f.write('')

        # append to log file
        with self.logfile.open('a') as f:
            f.write(text + '\n')

    def rm_log(self):
        ''' Delete log file.
        '''
        if self.logfile.exists():
            return self.logfile.unlink()

    #def print_table(self):
    #    ''' Print table showing how long each step took.
    #    '''
    #    print(f'{self.__class__.__name__} started {self[0].ts}: {self[0].msg}')
    #    for i, step in enumerate(self.steps[:-1]):
    #        print(f'    {step.ts}: (took {self[i+1].diff(step)}) {step.msg}')

        
@dataclass
class Step:
    _msg: str
    i: int
    ts: datetime = field(default_factory=datetime.now)
    mem: int = field(default_factory=lambda: psutil.virtual_memory().used)

    @property
    def msg(self):
        return self._msg if self._msg is not None else '.'

    def ts_diff(self, other: StepType):
        return (self.ts - other.ts).total_seconds()

    def format(self, prev_step: StepType = None, show_ts=True, show_delta=True, show_mem=True):
        if show_ts:
            ts_str = f"{self.ts.strftime('%a %H:%M:%S')}/"
        else:
            ts_str = ''

        if show_mem:
            mem_usage = f"{doctable.format_memory(self.mem):6}/"
        else:
            mem_usage = ''

        if show_delta and prev_step is not None:
            ts_diff = f"+{doctable.format_time(self.ts_diff(prev_step)):6}/"
        else:
            ts_diff = ''

        return f'{ts_str}{mem_usage}{ts_diff}{self.i:2}: {self.msg}'


