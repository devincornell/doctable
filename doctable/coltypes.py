import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np

class TokensType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return '\n'.join(value)
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.split('\n')
        else:
            return None

class SubdocsType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return '\n\n'.join(['\n'.join(vs) for vs in value])
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return tuple(
                tuple(v.split('\n')) 
                for v in value.split('\n\n')
            )
        else:
            return None
        
class SubsubdocsType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, ssdoc, dialect):
        '''Convert subsubdoc to string for storage.
        Args:
            ssdoc (list<list<str>>): subsubdoc to store into database.
                Might want to store lists of paragraphs as lists of sents
                as lists of tokens.
        Output:
            str: subsubdoc as string for storage
        '''
        if ssdoc is not None:
            return '\n\n\n'.join([
                '\n\n'.join([
                    '\n'.join(toks) for toks in sdoc
                ]) for sdoc in ssdoc
            ])
        else:
            return None

    def process_result_value(self, ssdocstr, dialect):
        '''Extract subsubdoc from database.
        Args:
            value (str): string where "\n\n\n" separates subdocuments,
                "\n\n" separates subsubdocuments and "\n" separates tokens.
        Output:
            list<list<str>>: list of list of tokens
        '''
        if ssdocstr is not None:
            return tuple(
                tuple(
                    tuple(sdocstr.split('\n')) # split into tokens
                    for sdocstr in ssdocstr.split('\n\n')
                )
                for ssdocstr in ssdocstr.split('\n\n\n')
            )
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

