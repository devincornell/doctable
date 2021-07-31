
import time
import random
import multiprocessing
import pytest

import sys
sys.path.append('..')
import doctable


def example_func(x, y = None):
    return x**y

def example_func2(x):
    return x + 'a'

def example_func3(x):
    return x + 1

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
    
    #worker.join()
    exit()

    x = doctable.DataPayload(2)
    worker = doctable.WorkerResource(kwargs=dict(y=2))
    worker.update_userfunc(example_func)
    worker.send_payload(x)
    xr = worker.recv()
    print(x, xr)
    worker.join()
    assert(example_func(x.data, y=2)==xr.data)
    

    worker1 = doctable.WorkerResource(userfunc=example_func2)
    worker2 = doctable.WorkerResource(userfunc=example_func3)


    worker1.send_payload(doctable.DataPayload(0))
    
    try:
        print(worker1.recv())
    except doctable.WorkerDiedError:
        worker1.join()
        worker2.join()



if __name__ == '__main__':
    test_workerresource()




