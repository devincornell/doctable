from multiprocessing import Pipe, Process
import os
import math

class Distribute:
    def __init__(self, workers=None):
        
        if workers is None:
            self.workers_og = os.cpu_count()
        else:
            self.workers_og = min([os.cpu_count(), workers])
        
        self.pool = None
        self.finished = True
        
    # for "with Distribute() as d:"
    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        # close all explicitly
        if self.pool is not None:
            for i in range(self.workers):
                self.pool[i].terminate()
        
        if not self.finished:
            raise RuntimeError('There was a problem with the chunk_thread.')
                
    def chunkmap(self, elements, chunk_thread, *thread_args):
        # mark as in-progress
        self.finished = False
        
        # set number of workers as minimum
        self.workers = min([len(elements), self.workers_og])        

        # chunk up elements
        chunk_size = math.ceil(len(elements)/self.workers)
        chunks = [elements[i*chunk_size:(i+1)*chunk_size]
                        for i in range(self.workers)]
        
        # create pool and pipes
        self.pipes = [Pipe(False) for i in range(self.workers)]
        self.pool = [Process(target=self._distribute_chunks_thread_wrap, 
            args=(chunk_thread, self.pipes[i][1], chunks[i], thread_args)) 
            for i in range(self.workers)]
        
        # init processes
        for i in range(self.workers):
            self.pool[i].start()

        # get data from self.pipes
        results = list()
        for i in range(self.workers):
            results.append(self.pipes[i][0].recv())
            
        # wait for processes to close
        for i in range(self.workers):
            self.pool[i].join()
        
        # no longer raise exception if there was a problem
        self.finished = True
        
        # un-chunk results
        results = [r for chunk_results in results for r in chunk_results]
        return results
        
    @staticmethod
    def _distribute_chunks_thread_wrap(func, pipe, chunk, staticdata):
        res = func(chunk, *staticdata)
        if isinstance(res, list) or isinstance(res, tuple):
            pipe.send(res)
        else:
            pipe.send([res]*len(chunk))
    
    
#class DManager:
#    def __init__
    
    