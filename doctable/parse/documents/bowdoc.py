
from collections import Counter
from .basedoc import BaseDoc

class TokenDoc(Counter):
    
    @property
    def toks(self):
        raise NotImplementedError()

