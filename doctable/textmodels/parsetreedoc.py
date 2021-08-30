
from typing import Any
from .basedoc import BaseDoc
from .parsetree import ParseTree

class ParseTreeDoc(list):
    ''' Represents a document composed of sequence of parsetrees.
    '''

    @property
    def tokens(self):
        return (t for pt in self for t in pt)

    def as_dict(self):
        ''' Convert document into a list of dict-formatted parsetrees.
        '''
        return [pt.as_dict() for pt in self]

    @classmethod
    def from_dict(cls, tree_data: list, *args, **kwargs):
        ''' Create new ParseTreeDoc from a dictionary tree created by as_dict().
        Args:
            tree_data: list of dict trees created from cls.as_dict()
        '''
        # root is reference to entire tree
        return cls(ParseTree.from_dict(ptd, *args, **kwargs) for ptd in tree_data)

    @classmethod
    def from_spacy(cls, doc: Any, *args, **kwargs):
        ''' Create a new ParseTreeDoc from a spacy Doc object.
        '''
        return cls(ParseTree.from_spacy(sent, *args, **kwargs) for sent in doc.sents)
    


