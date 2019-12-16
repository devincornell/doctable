import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np
from collections import Iterable
from random import randrange
import os

from .parsetree import ParseTree


class PickleFileType(types.TypeDecorator):
    impl = types.String
    
    def __init__(self, *arg, fpath=None, **kw):
        '''Define init to store fpath.'''
        if fpath is None:
            raise Exception('fpath must be defined when '
                'initializing PickleFileType.')
        self.fpath = fpath+'/'
        
        # make directory if it doesn't exist
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        
        types.TypeDecorator.__init__(self, *arg, **kw)

    def process_bind_param(self, value, dialect):
        if value is not None:
            while True:
                fname = os.path.join(self.fpath, '{}.pic'.format(randrange(10**11)))
                if not os.path.exists(fname):
                    break # after this, fname doesn't exist
            with open(fname, 'wb') as f:
                cPickle.dump(value,f)
            return os.path.basename(fname)
        else:
            return None

    def process_result_value(self, fname, dialect):
        if fname is not None:
            with open(os.path.join(self.fpath, fname), 'rb') as f:
                obj = cPickle.load(f)
            return obj
        else:
            return None



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

        
class ParseTreeType(types.TypeDecorator):
    impl = types.PickleType
    
    def process_bind_param(self, parsetree, dialect):
        if parsetree is not None:
            return recurse_store_pt(parsetree)
        else:
            return None

    def process_result_value(self, pt_dict, dialect):
        if pt_dict is not None:
            return recurse_load_pt(pt_dict)
        else:
            return None
    @staticmethod
    def recurse_store_pt(obj):
        if is_iter(obj):
            return [recurse_store_pt(el) for el in obj]
        elif isinstance(obj, ParseTree):
            return obj.asdict()
        else:
            return obj
    @staticmethod
    def recurse_load_pt(obj):
        if is_iter(obj):
            return [recurse_load_pt(el) for el in obj]
        elif isinstance(obj, dict):
            return ParseTree(obj)
        else:
            return obj
        
        
        
def is_iter(o):
    return isinstance(o,list) or isinstance(o,tuple) or isinstance(o,set)
        
        
