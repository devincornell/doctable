#import _pickle as cPickle
import pickle
import sqlalchemy.types as types
import numpy as np
from random import randrange
import os
import json

from .parsetree import ParseTree


class FileTypeBase(types.TypeDecorator):
    file_ext = None # needs to be overloaded
    impl = types.String # just stores filename
    fname_num_size = 10**12
    def __init__(self, *arg, fpath=None, **kw):
        '''Define init to store fpath.'''
        if fpath is None:
            raise Exception('fpath must be defined when '
                'initializing a file type.')
        self.fpath = fpath+'/'
        
        # make directory if it doesn't exist
        if not os.path.exists(fpath):
            os.mkdir(fpath)
        
        types.TypeDecorator.__init__(self, *arg, **kw)
        
    # NEEDS TO BE DEFINED IN INHERITING CLASS
    @classmethod
    def dump_data(cls, f, value, dialect):
        raise NotImplementedError
    @classmethod
    def load_data(cls, f, dialect):
        raise NotImplementedError
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            while True:
                fname = os.path.join(self.fpath, '{}{}'
                    ''.format(randrange(self.fname_num_size), self.file_ext))
                if not os.path.exists(fname):
                    break # after this, fname doesn't exist
            with open(fname, 'wb') as f:
                self.dump_data(f, value, dialect)
            return os.path.basename(fname)
        else:
            return None
    
    def process_result_value(self, fname, dialect):
        if fname is not None:
            with open(os.path.join(self.fpath, fname), 'rb') as f:
                obj = self.load_data(f, dialect)
            return obj
        else:
            return None


class PickleFileType(FileTypeBase):
    file_ext = '.pic'
    @classmethod
    def dump_data(cls, f, value, dialect): # used in FileTypeBase.process_bind_param()
        return pickle.dump(value, f, -1) # use highest protocol with negative number
    @classmethod
    def load_data(cls, f, dialect):
        return pickle.load(f)

class TextFileType(FileTypeBase):
    file_ext = '.txt'
    @classmethod
    def dump_data(cls, f, text, dialect): # used in FileTypeBase.process_bind_param()
        return f.write(text.encode())
    
    @classmethod
    def load_data(cls, f, dialect):
        return f.read().decode()

# NOTE: I SIMPLY HAVENT BOTHERED TO INTEGRATE THIS INTO CODE - SHOULD BE CORRECT THOUGH
class JSONFileType(FileTypeBase):
    file_ext = '.json'
    @classmethod
    def dump_data(cls, f, value, dialect): # used in FileTypeBase.process_bind_param()
        return json.dump(value, f, indent=2) # use highest protocol with negative number
    @classmethod
    def load_data(cls, f, dialect):
        return json.load(f)
    
    
    
    

class CpickleType(types.TypeDecorator):
    impl = types.LargeBinary
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return pickle.dumps(value, -1) # negative protocol number means highest
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return pickle.loads(value)
        else:
            return None
        
        
class JSONType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, indent=2, default=str) # coerce unknown types into strings
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        else:
            return None
        

        
class ParseTreeType(types.TypeDecorator):
    impl = types.PickleType
    
    def process_bind_param(self, parsetree, dialect):
        if parsetree is not None:
            return self.recurse_store_pt(parsetree)
        else:
            return None

    def process_result_value(self, pt_dict, dialect):
        if pt_dict is not None:
            return self.recurse_load_pt(pt_dict)
        else:
            return None
    @staticmethod
    def recurse_store_pt(obj):
        if is_iter(obj):
            return [self.recurse_store_pt(el) for el in obj]
        elif isinstance(obj, ParseTree):
            return obj.asdict()
        else:
            return obj
    @staticmethod
    def recurse_load_pt(obj):
        if is_iter(obj):
            return [self.recurse_load_pt(el) for el in obj]
        elif isinstance(obj, dict):
            return ParseTree(obj)
        else:
            return obj
        
        
        
def is_iter(o):
    return isinstance(o,list) or isinstance(o,tuple) or isinstance(o,set)
        
        
