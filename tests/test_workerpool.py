
import statistics
import time
import random
import multiprocessing
import pytest

import sys
sys.path.append('..')
import doctable

def example_func(x, y=2):
    return x**y

def example_sleep_func(x):
    time.sleep(x/100000)

def test_workerpool(n=100):
    
    pool = doctable.WorkerPool(1, verbose=False)
    assert(not pool.any_alive())
    pool.start()
    assert(pool.any_alive())
    print(pool)
    print(f'average efficiency: {pool.av_efficiency()}')
    pool.join()
    assert(not pool.any_alive())

    with pytest.raises(doctable.NoWorkersAvailable):
        pool.av_efficiency()

    with doctable.WorkerPool(3, verbose=False) as pool:
        assert(pool.any_alive())
        print(f'av efficiency: {pool.av_efficiency()}')

        # test most basic map function
        elements = list(range(100))
        assert(pool.map(example_func, elements) == [example_func(e) for e in elements])
        print(f'av efficiency: {pool.av_efficiency()}')

    elements = list(range(1000))
    with doctable.WorkerPool(3, verbose=False) as pool:
        pool.map(example_sleep_func, elements)
        print(f'av efficiency: {pool.av_efficiency()}')

if __name__ == '__main__':
    test_workerpool()
