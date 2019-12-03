import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np

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
            return parsetree.asdict()
        else:
            return None

    def process_result_value(self, pt_dict, dialect):
        if pt_dict is not None:
            return ParseTree(pt_dict)
        else:
            return None

class SpacyDocType(types.TypeDecorator):
    impl = types.PickleType
    
    def process_bind_param(self, doc, dialect):
        if doc is not None:
            return parsetree.asdict()
        else:
            return None

    def process_result_value(self, pt_dict, dialect):
        if pt_dict is not None:
            return ParseTree(pt_dict)
        else:
            return None
