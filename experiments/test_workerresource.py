

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
    time.sleep(x)

def test_workerresource(n=100):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''
    worker = doctable.WorkerResource(start=False, verbose=True)
    assert(not worker.is_alive())
    worker.start()
    assert(worker.is_alive())

    with pytest.raises(doctable.WorkerHasNoUserFunctionError):
        worker.execute(1)

    worker.update_userfunc(example_func, y=2)
    assert(worker.execute(1) == 1)
    assert(worker.execute(2) == 4)

    with pytest.raises(doctable.UserFuncRaisedException):
        worker.execute('a')

    worker.join()

    x = 5
    y = 2
    with doctable.WorkerResource(example_func, kwargs=dict(y=y)) as worker:
        worker.send_data(x)
        z = worker.recv_data()
        assert(z == x**y)

        y=3
        worker.update_userfunc(example_func, y=y)
        z = worker.execute(x)
        assert(z == x**y)

    y = 2
    with doctable.WorkerResource(example_sleep_func) as worker:
        print('started executing')
        ys = [worker.execute(i/100000) for i in range(100)]
        print('stopped executing')
        status = worker.get_status()
        print(status)
        print(status.efficiency(), status.total_efficiency(), status.sec_per_job())

    


if __name__ == '__main__':
    test_workerresource()
