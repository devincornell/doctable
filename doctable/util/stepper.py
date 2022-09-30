
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, TypeVar
import os
import psutil
import pathlib
import collections
import statistics
from .unit_format import format_time

import doctable

StepType = TypeVar('StepType')

class Stepper:
    """ Times a task.
    """
    def __init__(self, message: str = None, logfile=None, new_log=False, 
            verbose=True, show_ts=True, show_delta=True, show_mem=True):
        ''' Add single step for current datetime.
        '''
        self.show_ts = show_ts
        self.show_delta = show_delta
        self.show_mem = show_mem
        self.verbose = verbose
        self.logfile = pathlib.Path(logfile) if logfile is not None else None
        self.steps = list()
        self.enterstack = collections.deque()
        
        # create a new logfile if needed
        if new_log and self.logfile is not None:
            self.rm_log()

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
        # little printout to log if timer is just starting
        if not len(self) and self.logfile is not None:
            self.write_log(f"\n{'='*10} New Stepper {'='*10}")

        # create new step
        newstep = Step(message, len(self.steps))
        #print(f'making step: {newstep}')
        self.print_step(newstep)

        # add step
        self.steps.append(newstep)
        return newstep
    
    ######################## logging functionality ########################
    def print_step(self, step: StepType, verbose=None, **format_args):

        # apply defaults
        default_format_args = dict(show_ts=self.show_ts, show_delta=self.show_delta, 
                        show_mem=self.show_mem)
        format_args = {**default_format_args, **format_args}
        
        # execute format method
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

    ######################## logging functionality ########################
    def get_diff_stat(self, stat: str = 'mean', as_str: bool = False):
        '''Get stats on differences between time points.
        Args:
            stat: name of function in "statistics" module to call
        '''
        if not hasattr(statistics, stat):
            raise ValueError('The stat was not a function in the "statistics" module.')
        prev = self.first
        diffs = list()
        for t in self[1:]:
            diffs.append(t.ts_diff(prev))
            prev = t

        result = getattr(statistics, stat)(diffs)
        if as_str:
            return format_time(result)
        else:
            return result

    @classmethod
    def time_call(cls, func: Callable, *args, num_calls=1, as_str = False, **kwargs):
        ''' Time function call with 0.05 ms latency per call.
        '''
        timer = cls(verbose=False)
        timer = cls(verbose=False)
        for i in range(10):
            func(*args, **kwargs)
            timer.step()
        
        if as_str:
            mean = timer.get_diff_stat(stat='mean', as_str=True)
            med = timer.get_diff_stat(stat='median', as_str=True)
            stdev = timer.get_diff_stat(stat='stdev', as_str=True)
            return f'{mean} ({med}) ± {stdev}'
        else:
            return timer.get_diff_stat(stat='mean', as_str=False)

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

    def __sub__(self, other: StepType):
        return self.ts_diff(other)

    def ts_diff(self, other: StepType):
        return (self.ts - other.ts).total_seconds()

    def format(self, prev_step: StepType = None, show_ts=True, show_delta=True, show_mem=True):
        if show_ts:
            ts_str = f"{self.ts.strftime('%a %H:%M:%S')}/"
        else:
            ts_str = ''

        if show_mem:
            mem_usage = f"{doctable.format_memory(self.mem):>9}/"
        else:
            mem_usage = ''

        if show_delta:
            if prev_step is not None:
                ts_diff = f"+{doctable.format_time(self.ts_diff(prev_step)):>10}/"
            else:
                ts_diff = f'{" "*11}/'
        else:
            ts_diff = ''

        return f'{ts_str}{mem_usage}{ts_diff}{self.i:2}: {self.msg}'


