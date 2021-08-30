
import numpy as np
import cupy as cp
import dataclasses
import functools
import random
import time
import gc

#class BaseClass:
#    @classmethod
#    def _from_doctable_row(cls, *args, **kwargs):
#        return cls(*args, **kwargs)

import sys
sys.path.append('..')
import doctable

#class Test1:
#    __slots__ = ['a']
#    a: int = 5


@doctable.schema(repr=False)
class CustomClass:
    '''This is my doc.'''
    __slots__ = []
    a: int
    b: int = doctable.Col(5)
    c: int = doctable.Col()

    # example method
    def aplusb(self):
        return self.a + self.b

    def __repr__(self):
        return 'wtfever'


if __name__ == '__main__':

    timer = doctable.Timer()

    sc = CustomClass(10)

    # make sure it is a slots class
    assert(not hasattr(sc, '__dict__'))
    assert(sc.aplusb() == 15)
    assert(len(sc._doctable_as_dict()) == 2)


    exit()
    if True:
        sc = CustomClass(10)
        print(sc)
        print(sc._doctable_as_dict())
        print(hasattr(sc, '__repr__'))
        print(sc.__doc__)
        #print(sc.__slots__)
        print(getattr(sc, 'a'))
        assert(sc._uses_slots())
        exit()

    if False:
        timer.step('making random numbers')
        nums = [random.randrange(0, 100) for _ in range(100000000)]

        timer.step('creating objects')
        objs = [CustomClass(n) for n in nums]
        
        timer.step('garbage collecting')
        del nums
        gc.collect()
        
        timer.step('waiting')
        time.sleep(60)

        timer.step('ended')
        #print(sc.__class__)
        #print(sc.__slots__)





