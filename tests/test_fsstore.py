
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
    def __init__(self, size):
        self.payload = list(range(size))
    def __len__(self):
        return len(self.payload)

def benchmark_insert_read(timer, folder, save_every=None, num_records=None, record_size=None):

    timer.step(f'=================== STARTING NEW TEST ==================')
    fs = doctable.FSStore(folder, save_every=save_every)
    test_record = TestRecord(record_size)
    timer.step(f'======== {num_records} records of size {len(test_record)} saved in chunks of {fs.save_every} ========')

    timer.step(f'creating test records')
    records = [copy.deepcopy(test_record) for _ in range(num_records)]

    timer.step(f'writing records')
    for record in records:
        fs.insert(record)
    fs.dump_file()

    timer.step(f'reading records')
    records = fs.select_records()
    
    timer.step(f'deleting records')
    fs.delete_records()

    timer.step('finished test')
    return records

def speed_benchmark(folder='tmp'):
    timer = doctable.Timer('starting timer')


    settings = itertools.product([10, 50, 100], [1000, 50000], [1000, 10000])
    for s1, s2, s3 in settings:
        benchmark_insert_read(timer, folder, save_every=s1, num_records=s2, record_size=s3)

    timer.step('deleting all data')
    fs = doctable.FSStore(folder)
    fs.delete_all_completely(force=True)

    timer.step('finished!')    
    timer.print_table()


if __name__ == '__main__':
    speed_benchmark()
