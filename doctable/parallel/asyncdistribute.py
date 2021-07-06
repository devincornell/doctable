from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections

from .workerpool import WorkerPool
from .exceptions import WorkerDied

class AsyncDistribute:
    def __init__(self, num_workers: int, 
            func: Callable = None, start_workers: bool = True,
            *worker_args, **worker_kwargs):
        self.num_workers = num_workers
        
        # start workers
        self.pool = WorkerPool()
    
    def __del__(self):
        if self.pool.is_alive():
            self.pool.terminate()
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.pool.is_alive():
            self.pool.join()

    ####################### Process Management #######################
    def close_workers(self): 
        if self.pool.is_alive():
            self.pool.join()
    
    def start_workers(self, *args, func: Callable = None, **kwargs):
        '''Creates a new set of workers, removes old set if needed.
        '''
        if self.pool.is_alive():
            self.pool.update_userfunc(func)
        else:
            self.pool.start(self.num_workers, *args, func=func, **kwargs)
    
    ####################### Data Transmission #######################
    def map(self, func: Callable, elements: Iterable[Any], *args, **kwargs):

        was_alive = self.pool.is_alive()
        self.start_workers(*args, func=func, **kwargs)

        elem_iter = iter(elements)
        
        # send first data to each process
        ind = 0
        for worker in self.pool:
            try:
                nextdata = next(elem_iter)
            except StopIteration:
                break
            
            worker.send(ind, nextdata)
            ind += 1

        # send data to each process
        results = list()
        do_loop = True
        worker_died = False
        while do_loop or len(results) < ind:
            for worker in self.pool:
                if worker.poll():
                    try:
                        results.append(worker.recv())
                    except EOFError as e:
                        worker_died = True
                        do_loop = False
                        break
                    try:
                        nextdata = next(elem_iter)
                    except StopIteration:
                        do_loop = False
                        break
                
                    worker.send(ind, nextdata)
                    ind += 1

        if worker_died:
            raise WorkerDied(worker.pid)
        
        # sort results
        results = [r.data for r in sorted(results)]

        if not was_alive:
            self.close_workers()

        return results


