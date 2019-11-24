
import numpy as np

class DocBootstrap:
    def __init__(self, docs):
        self.docs = docs
        self.ids = None
    
    def get_doc_sample(self, n):
        '''Get list of bootstrapped sentences (doesn't make copy of bs sent ids).'''
        ids = self.get_sample(n)
        return [(idx, self.docs[idx]) for idx in ids]
    
    def get_sample(self, n):
        '''Randomly sample ids.'''
        return np.random.randint(len(self.docs), size=n)
        
    def draw_sample(self, n):
        '''Set random sample in bootstrap object.'''
        self.ids = self.get_sample(n)
    
    def get_docs(self):
        '''Returns sents which are sampled from ids drawn in .set_sample()'''
        if self.ids is None:
            raise ValueError('Need to call .draw_sample() before getting docs. '
                'Alternatively use .get_docs_single() to draw without setting sample.')
        
        return [(idx, self.docs[idx]) for idx in self.ids]
        

    

