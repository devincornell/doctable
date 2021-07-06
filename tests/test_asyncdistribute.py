import sys
sys.path.append('..')
import doctable
import time

import random

import multiprocessing

def test_func(x):
    return x**2

def test_asyncdistribute(n=100):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''
    test_input = list(range(n))
    

    with doctable.AsyncDistribute(2) as d:
        test_output = d.map(test_func, test_input)

    assert(test_output == list(map(test_func, test_input)))

if __name__ == '__main__':
    test_asyncdistribute()




