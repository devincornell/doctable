import sys
sys.path.append('..')
import doctable
import time

import random
import os
import multiprocessing

class TestWorker:
    def __init__(self, el):
        print(f'Calling init in pid={os.getpid()} with element ({el}).')

def test_play(n=1000):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''

    timer = doctable.Timer(logfile='logs/parallel_primefinder.log')

    timer.step('making elements')
    
    elements = list(range(3))
    with multiprocessing.Pool(24) as p:
        out = p.map(TestWorker, elements)

    print(out)
    
    exit()

    if False:
        test_func = find_prime_long
        elements = list(range(n))
        random.shuffle(elements)
    
    elif False:
        test_func = array_test

        import numpy as np
        elements = [np.ones((int(5e7)*(i+1),)) for i in range(10)]
        for a in elements:
            a[0] = 0
        print(len(elements), elements[0].shape)
        
    elif True:
        test_func = timed_step
        elements = list(range(n))
        random.shuffle(elements)

    timer.step('check ram')
    

    if False:
        timer.step('single-core eval')
        prime_single = list(map(test_func, elements))
 
    timer.step('multiprocessing.Pool')
    with multiprocessing.Pool(24) as p:
        prime_multi = p.map(test_func, elements)

    if False:
        timer.step('map_async')
        with multiprocessing.Pool(6) as p:
            prime_async = list(p.map_async(test_func, elements).get())
            
        timer.step('imap')
        with multiprocessing.Pool(6) as p:
            prime_imap = list(p.imap(test_func, elements, 100))

        timer.step('imap_unordered')
        with multiprocessing.Pool(6) as p:
            prime_unordered = list(p.imap_unordered(test_func, elements, 100))
    
    if False:
        timer.step('doctable.Distribute')
        with doctable.Distribute(24) as d:
            prime_distribute = d.map_chunk(test_func, elements)

    timer.step('doctable.WorkerPool')
    with doctable.WorkerPool(24) as p:
        prime_async = p.map(test_func, elements)
        print(f'av efficiency: {p.av_efficiency()}')

    timer.step('annnnndddd time!')
    
    assert(prime_multi == prime_async)

    timer.step('done')




if __name__ == '__main__':
    test_play()
