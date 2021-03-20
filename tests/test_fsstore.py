
from typing import List
from dataclasses import dataclass, field
import pytest
import os
import glob

import sys
sys.path.append('..')
import doctable

def test_basic():

    timer = doctable.Timer('starting tests')

    timer.step('init fsstore')
    fs = doctable.FSStore('tmp', save_every=100)

    timer.step('clearing all settings')
    fs.clear_settings()

    timer.step(f'current settings data: {fs.read_settings()}')

    timer.step(f'inserting unknown settings data.')
    with pytest.raises(KeyError):
        fs.write_settings(whateve='plz_don\'t_work')
    timer.step(f'current settings data: {fs.read_settings()}')
    
    # test resetting of seed
    timer.step('checking seed change')
    seed1 = fs.seed
    fs.set_seed()
    assert(seed1 != fs.seed)

    timer.step(f'deleting old records')
    fs.delete_records()

    timer.step(f'seed={fs.seed}; inserting records')

    records = [i for i in range(1000)]
    for r in records:
        fs.insert(r)

    fs.dump_file()

    timer.step('finished inserting; now checking integrity')
    assert(sum(records) == sum(fs.read_all_records()))

    timer.step('asserting deletion of records')
    fs.delete_records()
    assert(len(glob.glob(f'{fs.folder}/*.pic'))==0)


    timer.step('asserting deleted all completely!')
    fs.delete_all_completely()
    assert(not os.path.exists(fs.folder))

    



class TestRecord:
    ''' Record for testing data.'''
    def __init__(self, k=1000000):
        payload: list[int] = list(range(k))

def speed_benchmark():

    timer = doctable.Timer('starting tests')

    timer.step('creating data payload')
    record = TestRecord()

    timer.step('init fsstore')
    fs = doctable.FSStore('tmp', save_every=100)

if __name__ == '__main__':
    test_basic()
