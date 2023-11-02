
from .basedoc import BaseDoc

class SentTokenDoc(list):
    @property
    def toks(self):
        return (t for sent in self for t in sent)
