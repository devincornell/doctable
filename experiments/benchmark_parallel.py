import sys
sys.path.append('..')
import doctable
import time

import random

import multiprocessing

def find_prime(upper, lower=0):
    primes = list()
    for num in range(lower, upper + 1):
        # all prime numbers are greater than 1
        if num > 1:
            for i in range(2, num):
                if (num % i) == 0:
                    break
        else:
            primes.append(num)
    return primes

def find_prime_long(upper, lower=0):
    return [find_prime(upper, lower=lower) for _ in range(100)]

def find_prime_chunk(ns):
    return [find_prime(n) for n in ns]

def timed_test(num):
    time.sleep((num**2)/10000)

def timed_step(num):
    time.sleep(num/10)

def array_test(a):
    return a.dot(a)


def simple_primefinder(n=1000):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''

    timer = doctable.Timer(logfile='logs/parallel_primefinder.log')

    timer.step('making elements')

    if True:
        test_func = find_prime_long
        elements = list(range(n))
        random.shuffle(elements)
    else:
        test_func = array_test

        import numpy as np
        elements = [np.ones((int(5e7)*(i+1),)) for i in range(10)]
        for a in elements:
            a[0] = 0
        print(len(elements), elements[0].shape)

    timer.step('check ram')
    

    if False:
        timer.step('single-core eval')
        prime_single = list(map(test_func, elements))
 
    timer.step('multiprocessing.Pool')
    with multiprocessing.Pool(5) as p:
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

        timer.step('doctable.Distribute')
        with doctable.Distribute(6) as d:
            prime_distribute = d.map_chunk(test_func, elements)

    timer.step('doctable.WorkerPool')
    with doctable.WorkerPool(5) as p:
        prime_async = p.map(test_func, elements)
        print(f'av efficiency: {p.av_efficiency()}')

    timer.step('annnnndddd time!')
    
    assert(prime_multi == prime_async)

    timer.step('done')




if __name__ == '__main__':
    simple_primefinder()
