import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np


class CpickleType(types.TypeDecorator):
    impl = types.LargeBinary
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return cPickle.dumps(value)
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return cPickle.loads(value)
        else:
            return None


class TokensType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, tokens, dialect):
        if tokens is not None:
            return store_tokens(tokens)
        else:
            return None

    def process_result_value(self, tokstr, dialect):
        if tokstr is not None:
            return load_tokens(tokstr)
        else:
            return None

# =================== Token Storage Functions (recursive, so nessecarily functions) ===========

tok_mark = '\x1f' # unit separator (used to separate tokens)
storechars = (
    '\x1c', # file separator
    '\x1d', # group separator
    '\x1e', # record separator
    '\x0b', # vertical tab
)
# these are used because they are unlikeley to appear in documents submitted by the user
#http://www.asciitable.com/


def store_tokens(toktree, i=0, sep=storechars, tok_mark=tok_mark):
    '''Stores a set of nested tokens as a string, tokens are separated by special chars.'''
    if isinstance(toktree,str):
        #print('    '*i, 'token', toktree, '({:02x})'.format(ord(tok_mark)))
        return toktree + tok_mark
    
    #print('    '*i, toktree, '({:02x})'.format(ord(sep[i])))
    return ''.join(
        store_tokens(child, i+1, sep, tok_mark)
        for child in toktree
    ) + sep[i]


def load_l_tokens(treestr, i, sep, tok_mark):
    #print('  '*(i) + printhex(treestr), '({:02x})'.format(ord(sep[i])))
    if not treestr:
        return ()
    elif treestr[-1] == tok_mark:
        return tuple(treestr[:-1].split(tok_mark))
    children = treestr.split(sep[i])[:-1]
    return tuple(load_l_tokens(child, i+1, sep, tok_mark) for child in children)

def load_tokens(treestr, sep=storechars, tok_mark=tok_mark):
    '''Loads a set of nested tokens from a string. Opposite of store_tokens().'''
    return load_l_tokens(treestr, 0, sep, tok_mark)[0]

        

