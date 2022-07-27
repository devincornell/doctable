import numpy as np
import dataclasses
import functools
import random
import time
import gc
import pytest

import sys
sys.path.append('..')
import doctable

# THIS WILL FAIL
#class Test1:
#    __slots__ = ['a']
#    a: int = 5

@doctable.schema
class CustomClass:
    '''This is my doc.'''
    __slots__ = []
    a: int
    b: int = 5
    c: int = doctable.Col()

    # example method
    def aplusb(self):
        return self.a + self.b


if __name__ == '__main__':
    sc = CustomClass(10)

    # make sure it is a slots class
    assert(not hasattr(sc, '__dict__'))
    assert(sc.aplusb() == 15)
    assert(len(sc._doctable_as_dict()) == 2) # ignores EmptyValue
    assert(sc._uses_slots())
    assert(len(dataclasses.fields(sc)) == 3)
    
