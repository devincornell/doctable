

from .basedoc import BaseDoc

class TokenDoc(Counter, BaseDoc):
    
    @property
    def toks(self):
        raise NotImplementedError()

