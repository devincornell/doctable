import _pickle as cPickle
import sqlalchemy.types as types
import numpy as np

# separators for token, subdoc, and subsubdoc types
#http://www.asciitable.com/
tok_sep = '\x1f' # unit separator for splitting tokens
sdoc_sep = '\x1e' # record separator for splitting subdocs
ssdoc_sep = '\x1d' # group separator for splitting subsubdocs

class TokensType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, value, dialect):
        if value is not None:
            return tok_sep.join(value)+tok_sep
        else:
            return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.split(tok_sep)[:-1]
        else:
            return None

class SubdocsType(types.TypeDecorator):
    impl = types.String
    
    def process_bind_param(self, subdocs, dialect):
        if subdocs is not None:
            return sdoc_sep.join([tok_sep.join(sd)+tok_sep for sd in subdocs])+sdoc_sep
        else:
            return None

    def process_result_value(self, sdocstr, dialect):
        if sdocstr is not None:
            return [
                sdoc.split(tok_sep)[:-1]
                for sdoc in sdocstr.split(sdoc_sep)
            ][:-1]
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
            return ssdoc_sep.join([
                sdoc_sep.join([
                    ''.join([t+tok_sep for t in toks]) for toks in sdoc
                ])+sdoc_sep for sdoc in ssdoc
            ])+ssdoc_sep
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
            return [
                [
                    tokstr.split(tok_sep)[:-1]
                    for tokstr in sdocstr.split(sdoc_sep)[:-1]
                ]
                for sdocstr in ssdocstr.split(ssdoc_sep)[:-1]
            ]
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

