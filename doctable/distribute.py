from multiprocessing import Pipe, Process
import os
import math


class Distribute:
    def __init__(self, workers=None, override_maxcores=False):
        
        if workers is None:
            self.workers_og = os.cpu_count()
        else:
            if override_maxcores: # in case where user really wantes more workers than cores
                self.workers_og = workers
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
            print('thread exception traceback:', type, value, traceback)
            raise RuntimeError('There was a problem with the chunk_thread.')
    
    
    ########################### CHUNK PROCESSING ##########################
    def map_chunk(self, chunk_thread, elements, *thread_args):
        '''Applies chunk_thread to chunks of elements.
        '''
        
        # set number of workers as minimum
        self.workers = min([len(elements), self.workers_og])
        
        if self.workers <= 1:
            return chunk_thread(elements, *thread_args)
        else:
            # prepare to open processes
            self.finished = False
        
        # chunk up elements
        chunk_size = math.ceil(len(elements)/self.workers)
        chunks = [elements[i*chunk_size:(i+1)*chunk_size]
                        for i in range(self.workers)]
        
        # create pool and pipes
        self.pipes = [Pipe(False) for i in range(self.workers)]
        self.pool = [Process(target=self._map_chunk_thread, 
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
    def _map_chunk_thread(func, pipe, chunk, staticdata):
        # put some exception handling in here? This is a thread function
        res = func(chunk, *staticdata)
        if isinstance(res, list) or isinstance(res, tuple):
            pipe.send(res)
        else:
            pipe.send([res]*len(chunk))
        
    
    
    ########################### INSERT INTO DB ##########################
    ### NOTE I DIDN'T FINISH THIS PART - SOMETHIGN IS STILL WRONG!!!
    def map_insert(self, thread_func, elements, *thread_args, db=None):
        '''Map each element to be inserted in a doctable.
        Description: Used primairly to maintain one doctable instance
            per thread, but can have no other setup.
        Args:
            thread_func (func): applied to each element
            elements (list<>): list of elements
            thread_args: Additional args to be sent to each element
        '''
        was_connected = False
        if db is not None and db.engine.is_open():
            was_connected = True
            db.close_engine()
        
        results = self.map_chunk(self._map_insert_thread, 
                    elements, thread_func, db, *thread_args)
        
        if was_connected:
            db.open_engine()
        
        return results
        
    @staticmethod
    def _map_insert_thread(el_chunk, thread_func, db, *static_args):
        
        # open connection to doctable
        thread_args = list()
        if db is not None:
            db.open_engine(open_conn=True)
            thread_args.insert(0, db)
        
        # map thread_func to each elements, passing the doctable instance
        results = list()
        for element in el_chunk:
            results.append(thread_func(element, *thread_args, *static_args))
            
        if db is not None:
            db.close_engine()
        
        return results
#class DManager:
#    def __init__
    
    