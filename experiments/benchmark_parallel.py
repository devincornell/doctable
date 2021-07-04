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

def simple_primefinder(n=1000):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''

    timer = doctable.Timer(logfile='logs/parallel_primefinder.log')

    timer.step('making elements')
    elements = list(range(n))
    random.shuffle(elements)

    test_func = timed_test

    if False:
        timer.step('single-core find primes')
        prime_single = list(map(test_func, elements))

    timer.step('multi-core find primes')
    with multiprocessing.Pool(6) as p:
        prime_multi = p.map(test_func, elements)

    if False:
        timer.step('async find primes')
        with multiprocessing.Pool(6) as p:
            prime_async = list(p.map_async(test_func, elements).get())
            
        timer.step('imap find primes')
        with multiprocessing.Pool(6) as p:
            prime_imap = list(p.imap(test_func, elements, 100))

        timer.step('imap_unordered')
        with multiprocessing.Pool(6) as p:
            prime_unordered = list(p.imap_unordered(test_func, elements, 100))

        timer.step('doctable.Distribute')
        with doctable.Distribute(6) as d:
            prime_distribute = d.map_chunk(test_func, elements)

    timer.step('doctable.AsyncDistribute')
    with doctable.AsyncDistribute(6) as d:
        prime_async = d.map(test_func, elements)

    timer.step('done')




if __name__ == '__main__':
    simple_primefinder()
