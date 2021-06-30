from multiprocessing import Pipe, Process, Lock, Pool
import multiprocessing
import os
import dataclasses
from typing import Iterable, Callable, List, Dict, Any

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
    pipe: multiprocessing.Pipe
    def __call__(self, *args, **kwargs):
        '''Main loop.
        '''
        print('ARE WE ACTUALLY CALLING?')
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
            
    def send(self, payload: DataPayload):
        return self.pipe.send(payload)

    def receive_data(self):
        '''Tell main process that we're ready for more work.
        '''
        self.pipe.send(ReadyForWork(self.pid))
        return self.pipe.recv()

class AsyncWorkerPool:
    def __init__(self, num_workers: int):
        
        self.needs_work = None # keep track of workers that need jobs
        
        self.pipes = list()
        self.processes = list()
        for i in range(num_workers):
            main_pipe, worker_pipe = Pipe(True)
            self.pipes.append(main_pipe)
            
            self.processes.append(Process(
                name=f'worker_{i}',
                target=Worker(worker_pipe),
            ))

    ######################### Start/Stop Processes #########################
    def start(self):
        for p in self.processes:
            p.start()
        self.needs_work = dict()

    def join(self):
        for p in self.processes:
            p.join()
        self.needs_work = None
    
    def terminate(self):
        for p in self.processes:
            p.terminate()

    ######################### Send/Receive Data #########################
    def recv(self) -> DataPayload:
        for p in self.pipes:
            if p.poll():
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
