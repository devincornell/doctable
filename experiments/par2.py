from multiprocessing import Pipe, Process, Lock, Pool
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections



@dataclasses.dataclass
class Worker:
    '''Basic worker process.'''
    pipe: multiprocessing.Pipe
    def __call__(self):
        #print(f'Launched thread proces {os.getpid()}')
        self.pid = os.getpid()
        
        # send data right back
        while True:
            indata = self.pipe.recv()
            #print(f'proc {self.pid}: {indata}')
            self.pipe.send(indata)


class AsyncWorkerPool:
    def __init__(self, num_workers: int):
        
        self.pipes = list()
        self.procs = list()
        for i in range(num_workers):
            main_pipe, worker_pipe = Pipe(True)
            self.pipes.append(main_pipe)
            
            self.procs.append(Process(
                name=f'worker_{i}',
                target=Worker(worker_pipe),
            ))
        for proc in self.procs:
            proc.start()

    def __exit__(self, type, value, traceback):
        for proc in self.procs:
            proc.terminate()
    
    def __len__(self):
        return len(self.procs)
    
    def send_data(self, payload):
        payload = iter(payload)

        # use subset of processes if needed
        #procs, pipes = self.processes], self.pipes[use_proc]
        
        # send first data to each process
        for proc, pipe in zip(self.procs, self.pipes):
            print(f'getting next data for {proc.pid}')
            nextdata = next(payload)
            print(f'sending {nextdata} to {proc.pid}')
            pipe.send(nextdata)
            print(f'sent to {proc.pid}')

        datas = list()
        for pipe in self.pipes:
            if pipe.poll():
                datas.append()
        
        print('finished sending to processes')

        # wait for processes to close
        for proc in self.procs:
            proc.join()


if __name__ == '__main__':
    data = range(100)

    # create pool and pipes
    pool = AsyncWorkerPool(2)
    pool.send_data(range(100))
    print('waiting on processes')
