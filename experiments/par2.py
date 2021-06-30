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

class CloseWorkerSignal:
    pass


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
        self.terminate()
    
    def __len__(self):
        return len(self.procs)

    def terminate(self):
        for proc in self.procs:
            proc.terminate()
    
    def send_data(self, elements: Iterable[Any]):
        elem_iter = iter(elements)

        # use subset of processes if needed
        #procs, pipes = self.processes], self.pipes[use_proc]
        
        # send first data to each process
        ind = 0
        for proc, pipe in zip(self.procs, self.pipes):
            #print(f'getting next data for {proc.pid}')
            try:
                nextdata = next(elem_iter)
            except StopIteration:
                break
            #print(f'sending {nextdata} to {proc.pid}')
            pipe.send(DataPayload(ind, nextdata))
            ind += 1
            #print(f'sent to {proc.pid}')

        datas = list()
        do_loop = True
        while do_loop:
            for pipe in self.pipes:
                if pipe.poll():
                    datas.append(pipe.recv())
                    try:
                        nextdata = next(elem_iter)
                        ind += 1
                    except StopIteration:
                        do_loop = False
                        break
                    pipe.send(nextdata)
        
        print('finished sending to processes')
        print(datas)

        self.terminate()


if __name__ == '__main__':
    data = range(100)

    # create pool and pipes
    pool = AsyncWorkerPool(2)
    pool.send_data(range(100))
    print('waiting on processes')
