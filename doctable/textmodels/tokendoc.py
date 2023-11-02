
from .basedoc import BaseDoc

class TokenDoc(list):
    @property
    def toks(self):
        raise NotImplementedError
