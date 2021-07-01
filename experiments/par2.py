from multiprocessing import Pipe, Process, Lock, Pool
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections

@dataclasses.dataclass
class DataPayload:
    ind: int
    data: Any

class SigClose:
    pass


@dataclasses.dataclass
class Worker:
    '''Basic worker process.'''
    pipe: multiprocessing.Pipe
    def __call__(self):
        self.pid = os.getpid()
        
        # send data right back
        while True:
            indata = self.pipe.recv()
            if isinstance(indata, SigClose):
                break
            self.pipe.send(indata)


class AsyncWorkerPool:
    pipes = None
    procs = None
    def __init__(self, num_workers: int):
        self.num_workers = num_workers

    def __enter__(self):
        self.create_workers()

    def __exit__(self, type, value, traceback):
        pass

    def __del__(self):
        self.terminate()
    
    def __len__(self):
        return len(self.procs)


    ####################### Process Management #######################
    def create_workers(self):
        '''Creates and starts a new set of workers.
        '''
        self.pipes = list()
        self.procs = list()
        for i in range(self.num_workers):
            main_pipe, worker_pipe = Pipe(True)
            self.pipes.append(main_pipe)
            
            self.procs.append(Process(
                name=f'worker_{i}', 
                target=Worker(worker_pipe), 
            ))
        
        self.start()
        return self

    def start(self):
        if self.procs is not None:
            for proc in self.procs:
                proc.start()
        else:
            raise ValueError('Workers have not been created yet '
            '(call .start_workers() first).')

    def terminate(self):
        if self.procs is not None:
            for proc in self.procs:
                proc.terminate()
    
    def join(self):
        if self.procs is not None:
            for proc in self.procs:
                proc.send(SigClose())
                proc.join()
    
    ####################### Data Transmission #######################
    def map(self, elements: Iterable[Any]):
        elem_iter = iter(elements)
        
        # send first data to each process
        ind = 0
        for proc, pipe in zip(self.procs, self.pipes):
            try:
                nextdata = next(elem_iter)
            except StopIteration:
                break
            
            pipe.send(DataPayload(ind, nextdata))
            ind += 1

        results = list()
        do_loop = True
        while do_loop:
            for pipe in self.pipes:
                if pipe.poll():
                    results.append(pipe.recv())
                    try:
                        nextdata = next(elem_iter)
                        ind += 1
                    except StopIteration:
                        do_loop = False
                        break
                    pipe.send(nextdata)
        
        return [r.data for r in sorted(results, key=lambda x: x.ind)]


if __name__ == '__main__':
    data = range(100)

    # create pool and pipes
    pool = AsyncWorkerPool(2).create_workers()
    results = pool.map(range(100))
    
    print(len(results))

    print('waiting on processes')
