from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any, Tuple, NewType
import collections

from .workerresource import WorkerResource
from .exceptions import WorkerDied
from .worker import UserFuncArgs

class WorkerPool:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.workers = None
    
    def __del__(self):
        if self.is_alive():
            self.terminate()
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_workers()

    ####################### Process Management #######################
    def is_alive(self):
        return self.workers is not None and any([w.is_alive() for w in self])
    
    def start_workers(self, func: Callable = None, worker_args: UserFuncArgs = None):
        if self.is_alive():
            raise ValueError('This Pool already has running workers.')
        
        # start each worker
        for ind in range(self.num_workers):
            self.workers.append(WorkerResource(func=func, worker_args=worker_args, start=True))
        
        return self
    
    ############### Low-Level Process Operations ###############
    def join(self):
        if self.is_alive():
            [w.join() for w in self.workers]
            self.workers = None
        else:
            raise ValueError('Cannot join this pool because it has no workers.')
    
    def terminate(self): 
        if self.is_alive():
            [w.terminate() for w in self.workers]
            self.workers = None
        else:
            raise ValueError('Cannot join this pool because it has no workers.')
    
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


