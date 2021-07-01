from multiprocessing import Pipe, Process, Lock, Pool, Value
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections

@dataclasses.dataclass
class DataPayload:
    ind: int
    data: Any

@dataclasses.dataclass
class NewFunction:
    func: Callable

class SigClose:
    pass

no_function_error_msg = ('Worker {pid} was not provided '
    'with a function. Either provide a function when '
    'the worker is created or send a NewFunction via '
    'the pipe.')



@dataclasses.dataclass
class Worker:
    '''Basic worker process.'''
    pipe: multiprocessing.Pipe
    func: Callable = None
    def __call__(self):
        self.pid = os.getpid()
        
        # send data right back after processing
        while True:
            payload = self.pipe.recv()
            if isinstance(payload, DataPayload):
                if self.func is None:
                    raise ValueError(no_function_error_msg)
                payload.data = self.func(payload.data)
                self.pipe.send(payload)
            elif isinstance(payload, SigClose):
                break
            elif isinstance(payload, NewFunction):
                self.func = payload.func
            else:
                raise ValueError(f'Worker {self.pid} received '
                                        'unidentified object.')


class WorkerResource:
    '''Manages a worker process and pipe to it.'''
    def __init__(self, func: Callable, ind: int, *args):
        self.pipe, worker_pipe = Pipe(True)
        self.proc = Process(
            name=f'worker_{ind}', 
            target=Worker(worker_pipe, func), 
            args=args,
        )

class WorkerPool(list):

    ############### High-Level Process Operations ###############
    @classmethod
    def new_pool(cls, func: Callable, num_workers: int, *worker_args):
        newpool = cls()
        for ind in range(num_workers):
            newpool.append(WorkerResource(ind, func, *worker_args))
        newpool.start()
        return newpool

    def close(self):
        '''Close and kill worker processes.
        '''
        self.join()
        self.terminate()
    
    ############### Low-Level Process Operations ###############
    def start(self):
        for worker in self:
            worker.proc.start()
    
    def terminate(self):
        for worker in self:
            worker.proc.terminate()
    
    def join(self):
        for worker in self:
            worker.proc.send(SigClose())
            worker.proc.join()

class AsyncWorkerPool:
    workers = None
    def __init__(self, num_workers: int):
        self.num_workers = num_workers

    def __enter__(self):
        self.start_workers(self.num_workers)
        return self

    def __exit__(self, type, value, traceback):
        if self.workers is not None:
            self.workers.terminate()
        workers = None

    def __del__(self):
        if self.workers is not None:
            self.workers.terminate()

    ####################### Process Management #######################
    def start_workers(self, func: Callable = None, *worker_args):
        '''Creates and starts a new set of workers.
        '''
        self.workers.close()
        self.workers = WorkerPool.new_pool(func, self.num_workers, *worker_args)

    def close_workers(self):
        '''Close and kill worker processes.
        '''
        if self.workers is not None:
            self.workers.close()
        self.workers = None
    
    ####################### Data Transmission #######################
    def map(self, func: Callable, elements: Iterable[Any]):

        started_here = self.workers is None
        if started_here:
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
        results = [r.data for r in sorted(results, key=lambda x: x.ind)]

        return results


if __name__ == '__main__':
    data = range(100)

    # create pool and pipes
    pool = AsyncWorkerPool(2)
    results = pool.map(lambda x: x, range(100))
    
    print(len(results))

    print('waiting on processes')
