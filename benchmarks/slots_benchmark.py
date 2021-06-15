
import numpy as np
import cupy as cp
import dataclasses
import functools
import random
import time
import gc
import psutil
import itertools

import sys
sys.path.append('..')
import doctable

@doctable.row
class WithSlots:
    __slots__ = []
    id: int = doctable.IDCol()
    a: int = doctable.Col()
    b: int = doctable.Col(5)
    c: int = doctable.Col(10)
    d: int = doctable.Col(10)
    e: int = doctable.Col(10)
    f: int = doctable.Col(10)
    g: int = doctable.Col(10)
    h: int = doctable.Col(10)

@dataclasses.dataclass
class NoSlots(doctable.DocTableRow):
    id: int = doctable.IDCol()
    a: int = doctable.Col()
    b: int = doctable.Col(5)
    c: int = doctable.Col(10)
    d: int = doctable.Col(10)
    e: int = doctable.Col(10)
    f: int = doctable.Col(10)
    g: int = doctable.Col(10)
    h: int = doctable.Col(10)



def run_benchmark(timer, Cls, num_objs):

    timer.step(f'running with {num_objs=}, {Cls=}')

    pre_usage = psutil.virtual_memory().used

    timer.step('making random numbers')
    nums = [i for i in range(num_objs)]
    
    timer.step('\tcreating objects')
    objs = [Cls(n) for n in nums]

    timer.step('\tgarbage collecting nums from memory')
    del nums
    gc.collect()

    timer.step('\tchecking memory usage')
    post_usage = psutil.virtual_memory().used
    used_gb = (post_usage-pre_usage)/1e9
    print(f'{used_gb:0.2f} GB')
    
    return used_gb



if __name__ == '__main__':

    timer = doctable.Timer()

    #Cls = WithSlots
    #num_objs = int(10e6)
    nums = [int(5e5), int(1e6), int(5e6), int(10e6), int(20e6), int(50e6)]

    results = list()
    for Cls, num_objs in itertools.product([WithSlots, NoSlots], nums):
        results.append({
            'class': Cls.__name__,
            'num_objs': num_objs,
            'used_gb': run_benchmark(timer, Cls, num_objs),
        })


    timer.step('finished')

    import pandas as pd
    df = pd.DataFrame(results)
    print(df)

    import matplotlib.pyplot as plt
    plt.figure()
    #wdf = df['class'] == 'WithSlots'
    #ndf = df['class'] == 'NoSlots'
    #df.plot()
    df.pivot(index='num_objs', columns='class', values='used_gb').plot()
    #plt.plot()
    plt.savefig('results/slots_memory_usage.png')
    
