import numpy as np
import cupy as cp
import dataclasses
import functools
import random
import time
import gc
import pytest

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


@doctable.row(repr=False)
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











