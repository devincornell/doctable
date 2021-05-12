
from .basedoc import BaseDoc

class ParseTreeDoc(list, BaseDoc):
    
    @property
    def toks(self):
        return (t for sent in self for t in sent)

    


