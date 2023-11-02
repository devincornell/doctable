
from typing import List
from dataclasses import dataclass, field
import pytest
import os
import glob
import itertools
import copy

import sys
sys.path.append('..')
import doctable

def test_io():

    timer = doctable.Timer()

    obj = list(range(10000))
    fname = 'tmpfile.json_or_pic'

    timer.step('writing pickle')
    doctable.write_pickle(obj, fname)
    assert(os.path.exists(fname))

    timer.step('reading pickle')
    assert(obj == doctable.read_pickle(fname))
    os.remove(fname)

    timer.step('writing json')
    doctable.write_json(obj, fname)
    assert(os.path.exists(fname))

    timer.step('reading json')
    assert(obj == doctable.read_json(fname))

    os.remove(fname)
    timer.step('finished')


if __name__ == '__main__':
    test_io()
