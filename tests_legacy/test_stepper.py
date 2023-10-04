
from typing import List
from dataclasses import dataclass, field
import tempfile
import pytest

import sys
sys.path.append('..')
import doctable

import time

def test_timer():
    #tmp = doctable.TempFolder('logs')
    tmp = tempfile.TemporaryDirectory()

    stepper = doctable.Stepper(log_fname=f'{tmp}/1.log')
    stepper.step('running one thing')
    stepper.step()
    stepper.step('running last thing')
    assert(len(stepper) == 3)

    stepper = doctable.Stepper(log_fname=f'{tmp}/0.log')
    with stepper.step('Running test_func'):
        stepper.step()
    assert(len(stepper) == 3)


    stepper = doctable.Stepper(log_fname=f'{tmp}/2.log')
    with stepper.step('running loop') as start:
        stepper.step(f'{start.step.ts}')
        for i in range(100):
            stepper.step('start mem:', start.start_memory_str())
            stepper.step(f'{start.elapsed_str()=}, {start.memory_change_str()=}')

    k = 3
    for i in range(k):
        stepper.step(f'Hiya {i}!!')

    k = 3
    for i in stepper.tqdm(range(k)):
        stepper.step(f'Hiya {i}!!')
        for j in stepper.tqdm(range(k+2)):
            stepper.step(f'Hohoho {j}!')
    stepper.step()

    #mean = timer.get_diff_stat(stat='mean', as_str=False)
    #assert(mean >= 0.01 and mean < 0.011)

    #med = timer.get_diff_stat(stat='median', as_str=False)
    #assert(mean >= 0.01 and mean < 0.011)

    #stdev = timer.get_diff_stat(stat='stdev', as_str=False)
    #assert(stdev > 0 and stdev <= 0.001)
    #print(mean, med, stdev)

    #print(doctable.Stepper.time_call(lambda: time.sleep(0.001), num_calls=10))
    #print(doctable.Stepper.time_call(lambda: time.sleep(0.001), num_calls=10, as_str=True))



if __name__ == '__main__':
    test_timer()

