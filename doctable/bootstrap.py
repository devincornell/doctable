
import numpy as np

class DocBootstrap:
    def __init__(self, docs, n=None):
        self.docs = docs
        
        # set sample size
        if n is None:
            n = len(docs)
        self.n = n
        
        # draw initial sample
        self.ids = self._samp(n) # random ids
            
    def __iter__(self):
        return (self.docs[idx] for idx in self.ids)
    
    def set_new_sample(self, n=None):
        ''' Set internal sample state.
            Args:
                n (int): new number of samples to draw
        '''
        # set new number of samples
        if n is not None:
            self.n = n
        
        # draw new samples
        self.ids = self._samp(self.n)
        
    def new_sample(self, n=None, with_ids=False):
        ''' Save and return new sample.
        Args:
            n (int): number of new samples to draw. If None, will draw 
                previously set number.
            with_ids (bool): return (id,doc) tuples or just docs.
        '''
        # draw and save new sample
        self.set_new_sample(n)
        
        # return samples
        return self._retsamp(self.ids, with_ids)
        
    def _samp(self, n):
        '''Randomly sample ids.'''
        return np.random.randint(len(self.docs), size=n)
    
    def _retsamp(self, ids, with_ids):
        '''Return docs from given ids, either with or without ids.'''
        if with_ids:
            return [(idx, self.docs[idx]) for idx in ids]
        else:
            return [self.docs[idx] for idx in ids]
