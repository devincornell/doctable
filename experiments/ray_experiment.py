import numpy as np
import time
import sys
sys.setrecursionlimit(10000)

import ray
ray.init()

import doctable

class LLItem:
    def __init__(self, payload, n_items):
        self.payload = payload
        if n_items > 0:
            self.next = self.__class__(payload, n_items-1)
        else:
            self.next = None


@ray.remote
class Counter(object):
    def __init__(self, m):
        self.m = m
        self.value = 0

    def shape(self):
        time.sleep(20)
        return len(self.m)

    def increment(self, val=1):
        self.value += val

    def read(self):
        return self.value

def test_thread(ms):
    time.sleep(20)
    return [len(m) for m in ms]



if __name__ == '__main__':
    # 10 mil / 512 MB
    # 20 mil / 900 MB
    # 30 mil / 1285 MB
    # 40 mil / 1672 MB
    # 50 mil / 20158 MB
    with doctable.Timer('Making big array'):
        m = [i for i in range(30000000)]
    time.sleep(20)

    # Create an actor from this class
    print('the ray way')
    m = ray.put(m)
    counters = [Counter.remote(m) for _ in range(5)]
    print(ray.get([c.shape.remote() for c in counters]))
    del m
    del counters
    exit()
    
    # alternatively, use doctable
    print('old school way')
    mats = [m.copy() for _ in range(5)]
    with doctable.Distribute(1) as d:
        shapes = d.map_chunk(test_thread, mats)
    print(shapes)


    #counter = Counter.remote()
    #counter.increment.remote(10)
    #print(ray.get(counter.read.remote()))


