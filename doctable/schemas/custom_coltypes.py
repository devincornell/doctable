#import _pickle as cPickle
import pickle
import sqlalchemy.types as types
import numpy as np
from random import randrange
import os
import json
import pathlib
from doctable.textmodels import ParseTreeDoc

import dataclasses

class FileTypeControl:
    ''' All instances of FileTypeBase will have a reference to this object.
    '''
    select_raw_fname: bool = False
    def __init__(self, folder):
        if folder is None:
            raise Exception('folder must be defined when initializing '
                            'a file type.')
        self.path = pathlib.Path(folder)
        
        # make directory if it doesn't exist
        if not os.path.exists(self.path):
            os.mkdir(self.path)
    
    def __enter__(self):
        self.select_raw_fname = True
        return self
    
    def __exit__(self, *args):
        self.select_raw_fname = False

    def full_path(self, fname):
        return str(self.path.joinpath(fname))


class FileTypeBase(types.TypeDecorator):
    impl = types.String # just stores filename internally
    file_ext = None # needs to be overloaded
    
    fname_num_size = 10**12
    def __init__(self, *arg, folder=None, **kwargs):
        self.control = FileTypeControl(folder)
        types.TypeDecorator.__init__(self, *arg, **kwargs)

    @property
    def path(self):
        return self.control.path
        
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
                num = randrange(self.fname_num_size)
                fpath = self.control.full_path(f'{num}{self.file_ext}')
                if not os.path.exists(fpath):
                    break # after this, fpath doesn't exist
            with open(fpath, 'wb') as f:
                self.dump_data(f, value, dialect)
            return os.path.basename(fpath)
        else:
            return None
    
    def process_result_value(self, fname, dialect):
        if self.control.select_raw_fname:
            return self.control.full_path(fname)
        if fname is not None:
            with open(self.control.full_path(fname), 'rb') as f:
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

class ParseTreeDocFileType(FileTypeBase):
    file_ext = '_parsetreedoc.pic'
    @classmethod
    def dump_data(cls, f, value, dialect): # used in FileTypeBase.process_bind_param()
        return pickle.dump(value.as_dict(), f, -1) # use highest protocol with negative number
    @classmethod
    def load_data(cls, f, dialect):
        return ParseTreeDoc.from_dict(pickle.load(f))

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
        

        
#class ParseTreeType(types.TypeDecorator):
#    impl = types.PickleType
#    
#    def process_bind_param(self, parsetree, dialect):
#        if parsetree is not None:
#            return self.recurse_store_pt(parsetree)
#        else:
#            return None
#
#    def process_result_value(self, pt_dict, dialect):
#        if pt_dict is not None:
#            return self.recurse_load_pt(pt_dict)
#        else:
#            return None
#    @staticmethod
#    def recurse_store_pt(obj):
#        if is_iter(obj):
#            return [self.recurse_store_pt(el) for el in obj]
#        elif isinstance(obj, ParseTree):
#            return obj.asdict()
#        else:
#            return obj
#    @staticmethod
#    def recurse_load_pt(obj):
#        if is_iter(obj):
#            return [self.recurse_load_pt(el) for el in obj]
#        elif isinstance(obj, dict):
#            return ParseTree(obj)
#        else:
#            return obj
        
        
        
def is_iter(o):
    return isinstance(o,list) or isinstance(o,tuple) or isinstance(o,set)
        
        
