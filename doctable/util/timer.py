
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
import os

@dataclass
class Step:
    _msg: str = None
    _ts: datetime = field(default_factory=datetime.now)

    @property
    def msg(self):
        return self._msg if self._msg is not None else '.'

    @property
    def ts(self):
        ''' Formatted timestamp of given index.
        '''
        return self._ts.strftime('%a %H:%M:%S')
    
    def diff(self, other):
        delta = (self._ts - other._ts).total_seconds()

        if delta >= 3600:
            return f'{delta/3600:0.2f} hrs'
        elif delta >= 60:
            return f'{delta/60:0.2f} min'
        else:
            return f'{delta:0.2f} sec'

class Timer:
    """ Times a task. 
    """
    def __init__(self, message='', logfile=None, freshlog=True, verbose=True):
        ''' Add single step for current datetime.
        '''
        self.verbose = verbose
        self.logfile = logfile

        if logfile is not None and freshlog and os.path.exists(logfile):
            os.remove(logfile)
            with open(logfile, 'w') as f:
                f.write('')

        # add first timestamp
        self.steps = list()
        self.step(message)

    ######################## basic accessors ########################
    def __getitem__(self, ind):
        return self.steps[ind]

    ######################## enter/exit methods ########################
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self.step(verbose=False, save=True)
        if self.verbose:
            self._log(f'{self[0].msg} took {self[-1].diff(self[0])}.')
    
    ######################## main functionality ########################

    def step(self, message=None, **log_kwargs):
        ''' Add and log a new step.
        '''
        self.steps.append(Step(message))
    
        # log the new step
        if len(self.steps) == 1:
            self._log(f'START {self[-1].msg}', **log_kwargs)
        else:
            self._log(f'(prev took {self[-1].diff(self[-2])}) {self[-1].msg}', **log_kwargs)

    def _log(self, text, verbose=None, save=True):
        ''' Print and/or save, depending on settings. Possibly neither.
        '''
        ts = datetime.now().strftime('%a %H:%M:%S')
        output = f'{ts}: {text}'
        
        # print it
        if verbose or (verbose is None and self.verbose):
            print(output)
        
        # write to log file
        if self.logfile is not None and save:
            with open(self.logfile, 'a') as f:
                f.write(output + '\n')

    def total_diff(self):
        ''' Get time from first to last step.
        '''
        return self[-1].diff(self[0])

    def print_table(self):
        ''' Print table showing how long each step took.
        '''
        print(f'{self.__class__.__name__} started {self[0].ts}: {self[0].msg}')
        for i, step in enumerate(self.steps[:-1]):
            print(f'    {step.ts}: (took {self[i+1].diff(step)}) {step.msg}')

        


if __name__ == '__main__':
    print('starting')
    def test_func(n=100000000):
        return sum(i for i in range(n))
    
    with Timer('trying out enter and exit'):
        print(test_func())

    timer = Timer('testing verbose stepping')
    timer.step('running one thing')
    test_func()
    timer.step()
    test_func()
    timer.step('running last thing')

    timer = Timer('testing non-verbose stepping', verbose=False, logfile='../TMP.txt')
    print(test_func())

    timer.step('whatever this step is')
    print(test_func())

    timer.step('next step')
    print(test_func())

    timer.step('that\'s all folks.')
    timer.print_table()