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
    workers: List[WorkerResource] = None

    def __init__(self, num_workers: int, logging: bool = False, verbose: bool = False):
        self.num_workers = num_workers
        self.logging = logging
        self.verbose = verbose
    
    def __del__(self):
        self.terminate()
    
    def __enter__(self):
        if not self.any_alive():
            self.start_workers()
        return self

    def __exit__(self, *args):
        self.close_workers()

    ####################### Starting/Polling Workers #######################
    def any_alive(self):
        return self.workers is not None and any([w.is_alive() for w in self.workers])
    
    def start_workers(self, *worker_args, func: Callable = None, **worker_kwargs):
        if self.any_alive():
            raise ValueError('This Pool already has running workers.')
        
        # start each worker
        for _ in range(self.num_workers):
            self.workers.append(WorkerResource(
                func=func, 
                start=True, 
                verbose = self.verbose,
                logging = self.logging,
                args=worker_args, 
                kwargs=worker_kwargs,
            ))
        
        return self
    
    ####################### Data Transmission #######################
    def map(self, func: Callable, elements: Iterable[Any], *worker_args, **worker_kwargs):

        was_alive = self.any_alive()
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

    ############### Stopping Workers ###############
    def join(self):
        '''Attempt to join each worker, delete workers.'''
        if self.workers is not None:
            for w in self.workers:
                if w.is_alive():
                    w.join()
            self.workers = None
        else:
            raise ValueError('Cannot join this pool because it has no workers.')
    
    def terminate(self):
        '''Attempt to terminate each worker, delete workers.'''
        if self.workers is not None:
            for w in self.workers:
                if w.is_alive():
                    w.terminate()
            self.workers = None
        else:
            raise ValueError('Cannot terminate this pool because it has no workers.')
