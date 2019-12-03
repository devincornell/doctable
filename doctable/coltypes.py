import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np
from collections import Iterable

from .parsetree import ParseTree

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

        
def is_iter(o):
    return isinstance(o,list) or isinstance(o,tuple) or isinstance(o,set)
        
        
def recurse_store_pt(obj):
    if is_iter(obj):
        return [recurse_store_pt(el) for el in obj]
    elif isinstance(obj, ParseTree):
        return obj.asdict()
    else:
        return obj
        
def recurse_load_pt(obj):
    if is_iter(obj):
        return [recurse_load_pt(el) for el in obj]
    elif isinstance(obj, dict):
        return ParseTree(obj)
    else:
        return obj