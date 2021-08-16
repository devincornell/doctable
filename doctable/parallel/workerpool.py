from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any, Tuple, NewType
import collections
import statistics

from .exceptions import NoWorkersAvailable
from .workerresource import WorkerResource

@dataclasses.dataclass
class WorkerPool:
    num_workers: int
    logging: bool = True
    verbose: bool = False
    method: str = 'forkserver'
    workers: List[WorkerResource] = dataclasses.field(default_factory=list)

    def __post_init__(self):
        pass
    
    def __del__(self):
        self.terminate(check=False)
    
    def __enter__(self):
        if not self.any_alive():
            self.start()
        return self

    def __exit__(self, *args):
        self.join(check=False)

    def __getitem__(self, ind: int):
        return self.workers[ind]
    
    def __iter__(self):
        return iter(self.workers)

    ####################### Starting/Polling Workers #######################
    def any_alive(self):
        '''Check if any processes are alive.
        '''
        return self.workers is not None and any([w.is_alive() for w in self.workers])
    
    def start(self):
        '''Start workers.
        '''
        if self.any_alive():
            raise ValueError('This Pool already has running workers.')
        
        # start each worker
        for _ in range(self.num_workers):
            self.workers.append(WorkerResource(
                start=True, 
                verbose = self.verbose,
                logging = self.logging,
                method = self.method,
            ))
        
        return self

    def update_userfunc(self, func: Callable, args, kwargs):
        '''Update userfunction of all workers.
        '''
        self.apply(lambda w: w.update_userfunc(func, *args, **kwargs))

    ####################### Status Reporting #######################
    def get_statuses(self):
        '''Get statuses of each process (includes uptime, efficiency, etc).
        '''
        return self.apply(lambda w: w.get_status())

    def av_efficiency(self):
        '''Get average time spent working on jobs vs time spent waiting for new data.
        '''
        return statistics.mean([s.efficiency() for s in self.get_statuses()])
    
    def av_total_efficiency(self):
        '''Average time working on jobs vs lifetime of process.
        '''
        return statistics.mean([s.total_efficiency() for s in self.get_statuses()])

    def av_sec_per_job(self):
        '''Average number of seconds to complete each job.'''
        return statistics.mean([s.sec_per_job() for s in self.get_statuses()])
    
    ####################### Data Transmission #######################
    def map(self, func: Callable, elements: Iterable[Any], *worker_args, **worker_kwargs):

        self.update_userfunc(func, worker_args, worker_kwargs)

        # make an iterable to stream data
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

        return results

    ############### Stopping Workers ###############
    def join(self, check: bool = True):
        '''Attempt to join each worker, delete workers.
        '''
        self.apply(lambda w: w.join(), check=check)
        self.workers = None
    
    def terminate(self, check: bool = True):
        '''Attempt to terminate each worker, delete workers.
        '''
        self.apply(lambda w: w.terminate(), check=check)
        self.workers = None

    def apply(self, func: Callable, check: bool = True):
        '''Apply a function to each worker if it is alive.
        '''
        if self.workers is not None:
            results = list()
            for w in self.workers:
                if w.is_alive():
                    results.append(func(w))
            return results
        elif check:
            raise NoWorkersAvailable('whatever')
