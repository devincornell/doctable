
from doctable.parse.token import Token
import pickle
import typing

from functools import reduce

class DocTableExceptBase(Exception):
    def __init__(self):
        super().__init__(self.message)

class MissingSpacyPipelineComponent(DocTableExceptBase):
    message = 'Both the Spacy tagger and parser must be enabled to make a ParseTree.'

class TreeAlreadyAssigned(DocTableExceptBase):
    message = 'Current token already contains reference to a ParseTree.'

class ParseTree:
    ''' Represents a single parsetree.
    Properties:
        root (Token): reference to root of parsetree
        tokens list[Token]: ordered list of tokens
    '''
    def __init__(self, root_token: Token = None, overwrite_tree=False):
        '''Create from dict parsetree or spacy sentence root.
        Args:
            root_token (doctable.Token): root token of parsetree.
        '''
        # keep root token and assign reference back to this tree
        self.root = root_token
        self.propogate_tree_ref(self.root, overwrite=overwrite_tree)

        # create ordered sequence of tokens
        self.tokens = self.get_token_list()

    def propogate_tree_ref(self, tok, overwrite=False):
        ''' Recursively adds reference to current tree.
        Raises:
            TreeAlreadyAssigned: if the given token already 
                maintains a reference to another tree. A token
                can be assigned to only a single ParseTree.
        '''
        # make sure tree hasn't been assigned already
        if not overwrite and tok.tree is not None and tok.tree is not self:
            raise TreeAlreadyAssigned()
        
        # add reference recursively
        tok.set_tree(self)
        for child in tok.childs:
            self.propogate_tree_ref(child)

    def get_token_list(self):
        ''' Return ordered list of tokens.
        '''
        tokens = self.root.bubble_accum(lambda n: [n])
        return list(sorted(tokens, key=lambda n:n.i))

    ########################## Factory methods ##########################
    @classmethod
    def from_spacy(cls, spacy_sent: typing.Any, *args, **kwargs):
        ''' Create new parsetree from spacy doc.
        Args:
            spacy_sent: Spacy sent object.
            args: passed to Token.from_spacy()
            kwargs: passed to Token.from_spacy()
        '''
        # check if didn't use SpaCy dependency parser
        if not spacy_sent.root.doc.is_parsed:
            raise MissingSpacyPipelineComponent()

        # .root is reference to root token of sentence
        root = Token.from_spacy(spacy_sent.root, *args, **kwargs)
        return cls(root)

    @classmethod
    def from_dict(cls, root_tok_data: dict, *args, **kwargs):
        ''' Create new ParseTree from a dictionary tree created by as_dict().
        Args:
            root_tok_data: dict tree created from .as_dict()
        '''
        # root is reference to entire tree
        root = Token.from_dict(root_tok_data, *args, **kwargs)
        return cls(root)

    @classmethod
    def from_pickle(cls, pickle_data):
        return cls.from_dict(pickle.loads(pickle_data))
    
    ########################## Data serialization ##########################
    def as_dict(self):
        ''' Convert to a dictionary tree.
        '''
        return self.root.as_dict()

    def as_pickle(self):
        ''' Return a pickled dictionary tree.
        '''
        return pickle.dumps(self.as_dict())
        
    ########################## Basic accessors ##########################
    def token_texts(self):
        ''' List of token strings.
        '''
        return [n.text for n in self.tokens]
    
    ########################## Dunderscores ##########################
    def __str__(self):
        return f"{self.__class__.__name__}({' '.join(self.token_texts())})"
    
    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.root.__repr__())[1:-1]})'
        
    def __len__(self):
        ''' Number of tokens. '''
        return len(self.tokens)
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of tokens.'''
        return self.tokens[ind]
    
    def __iter__(self):
        ''' Iterate over tokens.'''
        return iter(self.tokens)
    
    ########################## Visualization ##########################
    def display(self, pad=15, base=10, **kwargs):
        ''' TODO Print out an ascii tree.
        '''
        self.print_tree_recursive(self.root, pad, base, **kwargs)
        
    @classmethod
    def print_tree_recursive(cls, tok, pad, base, level=0, root_str='{text}', dep_str=' -{dep}> {text}'):
        ''' TODO Printing tree for visualization.
        '''
        if level == 0:
            print(root_str.format(**tok.as_dict()).ljust(pad-(pad-base)), end='')
        else:
            print(dep_str.format(**tok.as_dict()).ljust(pad), end='')

        if len(tok.childs)==0: # base case
            print('\n' + ' '*(level*pad-(pad-base)), end='')
        else:
            for child in tok.childs:
                cls.print_tree_recursive(child, pad, base, level+1, root_str, dep_str)


