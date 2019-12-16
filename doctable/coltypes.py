import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np
from collections import Iterable
from random import randrange
import os

from .parsetree import ParseTree


class PickleFileType(types.UserDefinedType):
    
    # activate to return raw fname instead of file data
    _raw_fname_mode = False
    def set_raw_fname_mode(self, val=True):
        self._raw_fname_mode = val
    
    def __init__(self, fpath=None):
        print(hex(id(self)))
        if fpath is None:
            raise Exception('fpath must be defined when '
                'initializing PickleFileType.')
        self.fpath = fpath+'/'
        
        # make directory if it doesn't exist
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        
    def get_col_spec(self, **kw):
        return "VARCHAR"
    
    def bind_processor(self, dialect):
        self_fpath = self.fpath
        def process_bind_param(value):
            if value is not None:
                while True:
                    fname = self_fpath + '/{}.pic'.format(randrange(10**11))
                    if not os.path.exists(fname):
                        break # after this, fname doesn't exist
                with open(fname, 'wb') as f:
                    cPickle.dump(value,f)
                return os.path.basename(fname)
            else:
                return None
        return process_bind_param
    

    def result_processor(self, dialect, coltype):
        self_fpath = self.fpath
        self_raw_fname_mode = self._raw_fname_mode
        print('fname isnt none', self_raw_fname_mode, hex(id(self)))
        def process_result_value(fname):
            if fname is not None:
                if self_raw_fname_mode:
                    print('raw file mode')
                    return fname
                with open(self_fpath+'/'+fname, 'rb') as f:
                    obj = cPickle.load(f)
                return obj
            else:
                return None
        return process_result_value



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
        
        
