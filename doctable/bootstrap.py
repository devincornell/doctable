
import numpy as np

class DocBootstrap:
    def __init__(self, docs):
        self.docs = docs
        
    def sample(self, n):
        '''Yield bootstrapped sentences (doesn't make copy of bs sents).'''
        ids = np.random.randint(len(self.docs), size=n)
        for idx in ids:
            yield self.docs[idx]
    

