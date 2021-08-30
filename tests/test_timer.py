
from typing import List
from dataclasses import dataclass, field
import pytest
import os
import glob
import itertools
import copy

import sys
sys.path.append('..')
import doctable

import pathlib
import shutil
import time

def test_timer():
    tmp = doctable.TempFolder('logs')

    def test_func(sec=0.02):
        time.sleep(sec)
    #    return sum(i for i in range(n))
    
    
    with doctable.Timer('trying out enter and exit', logfile=tmp.path.joinpath('0.log')):
        test_func()

    timer = doctable.Timer('testing verbose stepping')
    timer.step('running one thing')
    test_func()
    timer.step()
    test_func()
    timer.step('running last thing')

    timer = doctable.Timer('testing non-verbose stepping', verbose=False, logfile=tmp.path.joinpath('2.log'))
    test_func()

    timer.step('whatever this step is')
    test_func()

    timer.step('next step')
    test_func()

    timer.step('that\'s all folks.')

    timer = doctable.Timer(verbose=False)
    for i in range(10):
        time.sleep(0.01)
        timer.step()
    
    mean = timer.get_diff_stat(stat='mean', as_str=False)
    assert(mean >= 0.01 and mean < 0.011)

    med = timer.get_diff_stat(stat='median', as_str=False)
    assert(mean >= 0.01 and mean < 0.011)

    stdev = timer.get_diff_stat(stat='stdev', as_str=False)
    assert(stdev > 0 and stdev <= 0.001)
    print(mean, med, stdev)

    print(doctable.Timer.time_call(lambda: time.sleep(0.001), num_calls=10))
    print(doctable.Timer.time_call(lambda: time.sleep(0.001), num_calls=10, as_str=True))



if __name__ == '__main__':
    test_timer()

