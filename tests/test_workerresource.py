

import time
import random
import multiprocessing
import pytest

import sys
sys.path.append('..')
import doctable

def example_func(x, y=2):
    return x**y

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

    y = 3    
    with doctable.WorkerResource(example_func, kwargs=dict(y=y)) as worker:
        worker.send_data(x)
        z = worker.recv_data()
        assert(z == x**y)


if __name__ == '__main__':
    test_workerresource()
