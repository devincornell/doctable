from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any, Tuple, NewType
import collections

from .workerresource import WorkerResource
from .exceptions import WorkerDied


class WorkerPool:
    def __init__(self, num_workers: int, 
            func: Callable = None, start_workers: bool = True,
            *worker_args, **worker_kwargs):
        self.num_workers = num_workers
        
        self.workers = None
        if start_workers:
            self.start(num_workers, func=func, args=(worker_args, worker_kwargs))
    
    def __del__(self):
        if self.pool.is_alive():
            self.terminate()
    
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_workers()

    ####################### Process Management #######################
    def is_alive(self):
        return self.workers is not None and all([w.is_alive() for w in self])
    
    def start(self, num_workers: int, func: Callable = None, worker_args: Tuple[Tuple, Dict[str,Any]]):
        if self.is_alive():
            raise ValueError('This Pool already has running workers.')
        
        # start each worker
        for ind in range(num_workers):
            self.workers.append(WorkerResource(ind, func=func, worker_args=args, start=True))
        
        return self

    def close_workers(self): 
        if self.is_alive():
            self.join()
    
    def start_workers(self, func: Callable = None, args=):
        '''Creates a new set of workers, removes old set if needed.
        '''
        if self.is_alive():
            self.pool.update_userfunc(func)
        else:
            self.pool.start(self.num_workers, *args, func=func, **kwargs)

    ############### Low-Level Process Operations ###############
    def join(self):
        [w.join() for w in self.workers]
        self.workers = None
    
    def terminate(self): 
        [w.terminate() for w in self.workers]
        self.workers = None
    
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


