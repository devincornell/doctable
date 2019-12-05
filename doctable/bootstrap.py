
import numpy as np

class DocBootstrap:
    def __init__(self, docs, n=None):
        self.n = n
        self.docs = docs
        self.ids = None
        
        if n is not None:
            self.ids = self._samp(n)
            
    def __iter__(self):
        if self.ids is None:
            raise ValueError('Need to call .set_sample(n) or provide a '
                'sample size to constructor.')
        return (self.docs[idx] for idx in self.ids)
            
            
    def set_sample(self, n=None):
        if n is None:
            n = self.n
        self.ids = self._samp(n)
        
    def sample(self, n=None, with_ids=False):
        '''Extract new sample if given n else return old sample.
        Args:
            n (int): number of new samples to draw. If None, will draw 
                sample from ids set by .set_sample().
            with_ids (bool): return (id,doc) tuples or just docs.
        '''
            
        if n is not None:
            # draw new sample
            ids = self._samp(n)
            return self._retsamp(ids, with_ids)
        
        else:
            # draw old sample
            if self.ids is None:
                raise ValueError('Need to specify n samples or call '
                    '.set_sample() first.')
            
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
