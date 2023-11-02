import random

import sys
sys.path.append('..')
import doctable

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


if __name__ == '__main__':
    elements = list(range(100))
    random.shuffle(elements)

    # create pool and pipes
    with doctable.AsyncDistribute(5) as d:
        results = d.map(find_prime, elements)
    
    print(len(results))
    print(results)
    print('waiting on processes')


