
from .token import Token
from functools import reduce

class ParseTree:
    root = None
    def __init__(self, root_node, *args, **kwargs):
        '''Create from dict parsetree or spacy sentence root.'''
        
        # check that spacy token is good
        if not isinstance(root_node, dict): # root node is spacy token
            if not root_node.doc.is_parsed:
                raise ValueError('Both the Spacy tagger and parser must '
                    'be enabled to make a ParseTree.')
        
        # root is reference to entire tree
        self.root = Token(root_node, *args, tree=self, **kwargs)
        _tokens = self.bubble_accum(lambda n: [n])
        self._tokens = list(sorted(_tokens,key=lambda n:n.i))
        
    @property
    def toks(self):
        ''' List of token texts.
        '''
        return [n.text for n in self._tokens]
        
    def __str__(self):
        return 'ParseTree({})'.format(self.toks)
    
    def __repr__(self):
        return str(self)
        
    def __len__(self):
        return len(self._tokens)
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of _tokens.'''
        return self._tokens[ind]
    
    def __iter__(self):
        return iter(self._tokens)
    
    def as_dict(self):
        return self.root.as_dict()
    
    def bubble_accum(self, func):
        '''Applies func to each node and bubbles up accumulated result (like reduce).
        Args:
            func (function): apply function to an object returning list.
        '''
        return self.root.bubble_accum(func)
    
    def bubble_reduce(self, func, init_data):
        '''Applies func to each node and bubbles up accumulated list of results.
        Args:
            func (function): apply function to an object returning list.
            init_data (any type): initial data to pass through reduce function
        '''
        return self.root.bubble_reduce(func, init_data)
    
    
    def display(self, pad=15, base=10, **kwargs):
        ''' Print out an ascii tree.
        '''
        self.print_tree_recursive(self.root, pad, base, **kwargs)
        
    @classmethod
    def print_tree_recursive(cls, tok, pad, base, level=0, root_str='{text}', dep_str=' -{dep}> {text}'):
        if level == 0:
            print(root_str.format(**tok.as_dict()).ljust(pad-(pad-base)), end='')
        else:
            print(dep_str.format(**tok.as_dict()).ljust(pad), end='')

        if len(tok.childs)==0: # base case
            print('\n' + ' '*(level*pad-(pad-base)), end='')
        else:
            for child in tok.childs:
                cls.print_tree_recursive(child, pad, base, level+1, root_str, dep_str)


