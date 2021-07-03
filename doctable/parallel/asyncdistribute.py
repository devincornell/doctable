from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections
from .workerpool import WorkerPool, DataPayload
from .exceptions import WorkerDied

class AsyncDistribute:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers
        self.workers = WorkerPool()

    def __del__(self):
        if self.workers.is_alive():
            self.workers.terminate()
    def __enter__(self): return self
    def __exit__(self, *args):
        if self.workers.is_alive():
            self.workers.close()

    ####################### Process Management #######################
    def close_workers(self): 
        if self.workers.is_alive():
            self.workers.close()
    def start_workers(self, func: Callable = None, *args, **kwargs):
        '''Creates a new set of workers, removes old set if needed.
        '''
        if self.workers.is_alive():
            self.workers.update_userfunc(func)
        else:
            self.workers.start(self.num_workers, func, *args, **kwargs)
    
    ####################### Data Transmission #######################
    def map(self, func: Callable, elements: Iterable[Any]):

        was_alive = self.workers.is_alive()
        self.start_workers(func)

        elem_iter = iter(elements)
        
        # send first data to each process
        ind = 0
        for worker in self.workers:
            try:
                nextdata = next(elem_iter)
            except StopIteration:
                break
            
            worker.send(ind, nextdata)
            ind += 1

        # send data to each process
        results = list()
        do_loop = True
        while do_loop:
            for worker in self.workers:
                if worker.poll():
                    try:
                        results.append(worker.recv())
                    except EOFError as e:
                        raise WorkerDied(worker.pid)
                    try:
                        nextdata = next(elem_iter)
                    except StopIteration:
                        do_loop = False
                        break
                    worker.send(DataPayload(ind, nextdata))
                    ind += 1
        
        # sort results
        results = [r.data for r in sorted(results)]

        if not was_alive:
            print(f'{was_alive=}')
            self.close_workers()

        return results


