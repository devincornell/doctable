from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections
from .workerpool import WorkerPool, DataPayload

class AsyncDistribute:
    def __init__(self, num_workers: int):
        self.workers = WorkerPool()

    def __del__(self): self.workers.terminate()
    def __enter__(self): return self
    def __exit__(self, type, value, traceback): self.workers.close()

    ####################### Process Management #######################
    def start_workers(self, func: Callable = None, *worker_args):
        '''Creates a new set of workers, removes old set if needed.
        '''
        if self.workers.is_open():
            raise ValueError('This pool already has workers.')
        self.close_workers()
        self.workers = WorkerPool.new_pool(func, self.num_workers, *worker_args)

    def close_workers(self):
        '''Close and kill worker processes.
        '''
        if not self.has_workers():
            raise ValueError('This pool does not have workers.')
        self.workers = None
    
    ####################### Data Transmission #######################
    def map(self, func: Callable, elements: Iterable[Any]):

        if not self.has_workers():
            self.start_workers()

        elem_iter = iter(elements)
        
        # send first data to each process
        ind = 0
        for worker in self.workers:
            try:
                nextdata = next(elem_iter)
            except StopIteration:
                break
            
            worker.send(DataPayload(ind, nextdata))
            ind += 1

        # send data to each process
        results = list()
        do_loop = True
        while do_loop:
            for worker in self.workers:
                if worker.poll():
                    results.append(worker.recv())
                    try:
                        nextdata = next(elem_iter)
                    except StopIteration:
                        do_loop = False
                        break
                    worker.send(DataPayload(ind, nextdata))
                    ind += 1
        
        # sort results
        results = [r.data for r in sorted(results)]

        return results


if __name__ == '__main__':
    data = range(100)

    # create pool and pipes
    pool = AsyncDistribute(2)
    results = pool.map(lambda x: x, range(100))
    
    print(len(results))
    print('waiting on processes')
