import sys
sys.path.append('..')
import doctable

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

def find_prime_chunk(ns):
    return [find_prime(n) for n in ns]


def simple_primefinder(n=5000):
    '''Tests ability to solve tasks when tasks take an 
        unequal ammount of time to execute.
    '''

    timer = doctable.Timer(logfile='parallel_primefinder.log')

    timer.step('making elements')
    elements = list(range(n))
    random.shuffle(elements)

    timer.step('single-core find primes')
    prime_single = list(map(find_prime, elements))

    timer.step('multi-core find primes')
    with multiprocessing.Pool(6) as p:
        prime_multi = p.map(find_prime, elements)

    timer.step('async find primes')
    with multiprocessing.Pool(6) as p:
        prime_async = list(p.map_async(find_prime, elements).get())
        
    timer.step('imap find primes')
    with multiprocessing.Pool(6) as p:
        prime_imap = list(p.imap(find_prime, elements, 100))

    timer.step('imap_unordered')
    with multiprocessing.Pool(6) as p:
        prime_unordered = list(p.imap_unordered(find_prime, elements, 100))

    timer.step('doctable.Distribute')
    with doctable.Distribute(6) as d:
        prime_distribute = d.map_chunk(find_prime_chunk, elements)
    timer.step('done')




if __name__ == '__main__':
    simple_primefinder()
