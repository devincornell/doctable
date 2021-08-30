import sys
sys.path.append('..')
import doctable
import time

import random

import multiprocessing

def example_func(x):
    return x**2

@doctable.slots_dataclass
class A:
    __slots__ = []
    a: int
    b: int = 0

def test_slots_dataclass(n=100):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''
    t1, t2 = A(1, 2), A(1, 3)
    print(t1, t2)
    assert(not hasattr(t1, '__dict__'))

if __name__ == '__main__':
    test_slots_dataclass()




