from multiprocessing import Pipe, Process, Lock, Pool
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any
import collections

@dataclasses.dataclass
class ReadyForWork:
    pid: int

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
    def __call__(self, *args, **kwargs):
        '''Main loop.
        '''
        print(f'Launch thread proces {os.getpid()}')
        # get process id
        self.pid = os.getpid()
        
        # tell main process that we're ready for data, get it
        outputs = list()
        while True:
            newdata = self.receive_data()
            if isinstance(newdata, DataPayload):
                # call function and send output back
                output = func(newdata, *args, **kwargs)
                self.send(DataPayload(ind=newdata.ind, data=output))

            # desire to kill worker
            elif isinstance(newdata, CloseWorkerSignal):
                break
                
            else:
                raise ValueError(f'Did not recognized received object type: {type(newdata)}')

        exit(0) # close thread


class WorkManager:
    '''Sends/receives data to/from workers.'''
    def __init__(self, manager_pipe: Pipe, worker_pipes: List[Pipe]):
        self.in_pipe = manager_pipe
        self.worker_pipes = worker_pipes

    def __call__(self, *args, **kwargs):
        worker_init = set()
        while True:
            # first get new data element, block until receive
            if self.in_pipe.poll():
                recvdata = self.in_pipe.recv()
            else:
                newdata = None

            # wait for worker to be available
            for i, p in enumerate(self.worker_pipes):
                if p.poll() or i not in worker_init:
                    olddata = p.recv()
                    worker_init.add(i)

        
    def get_ready_workers(self):
        for p in self.worker_pipes:
            if p.poll():
                pass


    def send(self, payload: Any):
        '''Send data to available worker.'''
        for p in self.worker_pipes:
            if p.poll():
                return p.recv()

    


class AsyncWorkerPool:
    def __init__(self, num_workers: int):
        self.queue = collections.deque()
        
        self.pipes = list()
        self.processes = list()
        for i in range(num_workers):
            main_pipe, worker_pipe = Pipe(True)
            self.pipes.append(main_pipe)
            
            self.processes.append(Process(
                name=f'worker_{i}',
                target=Worker(worker_pipe),
            ))

    def map_chunk(self, items: Iterable) -> Iterable:
        for item in items:
            pass

    ######################### Start/Stop Processes #########################
    def start(self):
        for p in self.processes:
            p.start()

    def join(self):
        for p in self.processes:
            p.join()
        self.needs_work = None
    
    def terminate(self):
        for p in self.processes:
            p.terminate()

    ######################### Send/Receive Data #########################
    def add_send(self, payload: DataPayload):
        '''Add to send queue.
        '''
        self.queue.append(payload)

    def recv(self) -> DataPayload:
        for p in self.pipes:
            return p.recv()


@staticmethod
def _map_chunk_thread(func, pipe, chunk, staticdata):
    # put some exception handling in here? This is a thread function
    res = func(chunk, *staticdata)
    if isinstance(res, list) or isinstance(res, tuple):
        pipe.send(res)
    else:
        pipe.send([res]*len(chunk))

if __name__ == '__main__':

    # only one thread can print at a time
    #printlock = Lock()
    #pipes = [Pipe(False) for i in range(n)]
    #p_main, p_worker = Pipe(True)
    #p = Process(target=worker, args=(p_worker,))
    pool = AsyncWorkerPool(2)
    exit()
    pool.start()
    
    import time
    time.sleep(0.1)
    while True:
        print(pool.recv())
    #for p in pool.pipes:
    #    if p.poll():
    #        print(p.recv())
    #    else:
    #        print('got nothing')
    pool.join()
