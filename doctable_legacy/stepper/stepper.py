
import time
from datetime import datetime
#from dataclasses import dataclass, field
import dataclasses
from typing import Callable, List, Dict, Any, TypeVar
import os
import psutil
import pathlib
import collections
import statistics
import tqdm

from ..util import format_memory, format_time
from .step import Step
import typing
from .errors import *
from .stepcontext import StepContext

@dataclasses.dataclass
class Stepper:
    """ Record information and output info as script progresses."""
    log_fname: str = None
    name: str = None
    new_log: bool = False
    verbose: bool = True
    show_ts: bool = True
    show_delta: bool = True
    show_mem: bool = True
    using_tqdm: bool = False
    init_step: Step = dataclasses.field(default_factory=Step.now)
    steps: typing.List[Step] = dataclasses.field(default_factory=list)
    ctx_stack: typing.List[StepContext] = dataclasses.field(default_factory=list)
    
    def __post_init__(self):
        # create a new logfile if needed
        self.log_fpath = pathlib.Path(self.log_fname) if self.log_fname is not None else None
        
        if self.new_log and self.log_fname is not None:
            self.rm_log()

        #self.default_format_kwargs = dict(
        #    show_ts=self.show_ts, 
        #    show_delta=self.show_delta, 
        #    show_mem=self.show_mem
        #)
        
    ######################## basic accessors ########################
    def __len__(self):
        return len(self.steps)
    
    def __getitem__(self, ind) -> Step:
        return self.steps[ind]
    
    def __iter__(self) -> typing.Iterable[Step]:
        return iter(self.steps)
    
    @property
    def last(self) -> Step:
        try:
            return self[-1]
        except KeyError:
            raise NoStepsAvailable(f'Cannot access .last: {self.__class__.__name__} has no steps.')

    @property
    def first(self) -> Step:
        try:
            return self[0]
        except KeyError:
            raise NoStepsAvailable(f'Cannot access .first: {self.__class__.__name__} has no steps.')
    
    ######################## main functionality ########################
    def step(self, message: str = None, verbose: bool = None, **format_kwargs) -> StepContext:
        ''' Add a new step, print and log it if needed.
        '''
        verbose = verbose if verbose is not None else self.verbose
        
        # little printout to log if timer is just starting
        if not len(self.steps) and self.log_fpath is not None:
            self.write_log(f"\n\n{'='*10} New Stepper {'='*10}\n")

        # create new step
        newstep = Step.now(i=len(self.steps), msg=message)        
        self.print_step(newstep, verbose=verbose, **format_kwargs)

        # add step
        self.steps.append(newstep)
        return StepContext(self, newstep, format_kwargs)
    
    
    ######################## logging functionality ########################
    def print_step(self, step: Step, verbose: bool = None, **format_kwargs):
        '''Write to log and print to screen if needed.'''
        verbose = verbose if verbose is not None else self.verbose
        
        # execute format method
        prev_step = self.steps[step.i-1] if len(self.steps) else None
        out_str = self.format_step_str(step, prev_step=prev_step, **format_kwargs)
        
        if self.using_tqdm:
            out_str = f'\n{out_str}'
            self.using_tqdm = False
        
        # write to log if enabled
        if self.log_fpath is not None:
            self.write_log(out_str)
        
        # print to output if requested
        if verbose:
            print(out_str)

    def write_log(self, text: str):
        ''' Write text to log file.
        '''
        # create new log file if does not exist
        if not self.log_fpath.exists():
            self.log_fpath.parents[0].mkdir(parents=True, exist_ok=True)
            with self.log_fpath.open('w') as f:
                f.write('')

        # append to log file
        with self.log_fpath.open('a') as f:
            f.write(text + '\n')

    def rm_log(self):
        ''' Delete log file.
        '''
        if self.log_fpath.exists():
            return self.log_fpath.unlink()

    def format_step_str(self, step: Step, prev_step: Step = None, show_ts=True, show_delta=True, show_mem=True) -> str:
        
        # helper to get a default value
        get_default = lambda x,y: x if x is not None else y
        
        if get_default(show_ts, self.show_ts):
            ts_str = f"{step.ts.strftime('%m/%d %H:%M:%S')}/"
        else:
            ts_str = ''

        if get_default(show_mem, self.show_mem):
            mem_usage = f"{format_memory(step.mem_bytes):>9}/"
        else:
            mem_usage = ''

        if get_default(show_delta, self.show_delta):
            if prev_step is not None:
                ts_diff = f"+{format_time(step.ts_diff(prev_step)):>10}/"
            else:
                ts_diff = f'{" "*11}/'
        else:
            ts_diff = ''

        return f'{ts_str}{mem_usage}{ts_diff}{step.i:2}: {step.msg}'


    ######################## for handling tqdm ########################
    def tqdm(self, *args, **kwargs):
        self.using_tqdm = True
        return tqdm.tqdm(*args, **kwargs)

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
    def time_call(cls, func: Callable, *args, num_calls: int = 1, as_str: bool = False, **kwargs):
        ''' Time function call with 0.05 ms latency per call.
        '''
        timer = cls(verbose=False)
        timer = cls(verbose=False)
        for i in range(num_calls):
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

        



