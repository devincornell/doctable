

import doctable
import pickle
import typing

from functools import reduce

class MissingSpacyPipelineComponent(Exception):
    message = 'Both the Spacy tagger and parser must '
                    'be enabled to make a ParseTree.'
    def __init__(self):
        super().__init__(self.message)

class ParseTree:
    root = None
    def __init__(self, root_token: doctable.Token):
        '''Create from dict parsetree or spacy sentence root.
        Args:
            root_token: root token of parsetree.
        '''
        self.root = root_token

        # create ordered sequence of tokens
        self.tokens = self.get_token_list()

    ########################## Factory methods ##########################
    def from_spacy(self, spacy_sent: typing.Any, *args, **kwargs):
        ''' Create new parsetree from spacy doc.
        Args:
            spacy_sent: Spacy sent object.
            args: passed to Token.from_spacy()
            kwargs: passed to Token.from_spacy()
        '''
        # check if didn't use SpaCy dependency parser
        if not root_node.doc.is_parsed:
            raise MissingSpacyPipelineComponent()

        # root is reference to root token
        self.root = doctable.Token.from_spacy(sent.root, *args, tree=self, **kwargs)
        
        # also store an ordered sequence of tokens
        self.get_token_list()

    def from_dict(self, root_tok_data: dict, *args, **kwargs):
        ''' Create new ParseTree from a dictionary tree created by as_dict().
        Args:
            root_tok_data: dict tree created from .as_dict()
        '''
        # root is reference to entire tree
        self.root = doctable.Token.from_dict(root_tok_data, *args, tree=self, **kwargs)
        

    def get_token_list(self):
        ''' Return ordered list of tokens.
        '''
        tokens = self.root.bubble_accum(lambda n: [n])
        return list(sorted(tokens, key=lambda n:n.i))

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
    @property
    def toks(self):
        ''' List of token strings.
        '''
        return [n.text for n in self.tokens]
    
    ########################## Dunderscores ##########################
    def __str__(self):
        return f"[{', '.join([str(t) for t in self.toks])}]"
    
    def __repr__(self):
        return 'ParseTree({})'.format(', '.join([t.__repr__() for t in self.toks]))
        
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


