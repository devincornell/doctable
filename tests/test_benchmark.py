
from typing import List
from dataclasses import dataclass, field
import tempfile
import pytest

import sys
sys.path.append('..')
import doctable

import time

def test_benchmark():
        
    print(doctable.Benchmark.time_func_call(time.sleep, args=(0.05,), num_calls=1))
    print(doctable.Benchmark.time_func_call(time.sleep, args=(0.05,), num_calls=3))



if __name__ == '__main__':
    test_benchmark()

