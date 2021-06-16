
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

    def test_func(sec=0.2):
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


if __name__ == '__main__':
    test_timer()

