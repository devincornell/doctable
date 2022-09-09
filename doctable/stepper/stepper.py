from __future__ import annotations

import time
#from datetime import datetime
import datetime
import dataclasses
from typing import Callable, List, Dict, Any, TypeVar
import pathlib
import collections
import statistics
import psutil

import doctable

from .step import Step

@dataclasses.dataclass
class StepContext:
    stepper: Stepper
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


class Stepper:
    '''Replaces Timer: logs info about script progresion.'''

    def __init__(self, name: str = None, logfile=None, new_log=False, 
            verbose=True, show_ts=True, show_delta=True, show_mem=True):
        ''' Add single step for current datetime.
        '''
        self.name = name
        self.logfile = pathlib.Path(logfile) if logfile is not None else None
        
        self.show_ts = show_ts
        self.show_delta = show_delta
        self.show_mem = show_mem
        self.verbose = verbose
        
        self.steps = list()
        self.init_step = Step.now()
        self.context_stack = collections.deque()
        
        # create a new logfile if needed
        if new_log and self.logfile is not None:
            self.rm_log()

        # add first timestamp (don't print star)
        #self.step(verbose=message is not None)

    ######################## basic accessors ########################
    def __len__(self):
        return len(self.steps)
    
    def __getitem__(self, ind: int) -> Step:
        return self.steps[ind]
    
    @property
    def last(self):
        return self.steps[-1]

    @property
    def first(self):
        return self.steps[0]

    ######################## enter/exit methods ########################
    #def __enter__(self):
    #    self.context_stack.append(self.last)
    #    return self
    #    
    #def __exit__(self, *args):
    #    start = self.context_stack.pop()
    #    end = self.step(f'END {start.msg}')
    
    ######################## main functionality ########################
    def step(self, message: str = None, verbose: bool = None, pid: int = None, **format_args) -> StepContext:
        ''' Add a new step, print and log it if needed.
        '''
        # create new step
        new_step = Step.now(msg=message, i=len(self.steps), pid=pid)
        
        # log it
        self.log_step(new_step, verbose=verbose)

        # add step
        self.steps.append(new_step)
        
        return StepContext(self, new_step)

    
    ######################## logging functionality ########################
    def log_step(self, step: Step, verbose: bool = None, **format_args):
        '''Add this step to the log and print to screen if requested.
        '''
        if not len(self) and self.logfile is not None:
            self.write_log(f"\n{'='*10} New Timer {'='*10}")
        
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
            return doctable.util.format_time(result)
        else:
            return result

    @classmethod
    def time_call(cls, func: Callable, *args, num_calls=1, as_str = False, **kwargs):
        ''' Time function call with 0.05 ms latency per call.
        '''
        timer = cls(verbose=False)
        timer = doctable.Timer(verbose=False)
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


