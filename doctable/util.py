

import pickle

#import sqlalchemy as sa
from .connectengine import *

def list_tables(target=':memory:', dialect='sqlite', **engine_args):
    ''' List tables in an sqlite database.
    Args:
        target (str): sql file or endpoint to connect to
        dialect (str): sql dialect to use for conenction
        engine_args (kwargs): passed to sqlalchemy ConnectEngine
    '''
    engine = ConnectEngine(target=target, dialect=dialect, **engine_args)
    return engine.list_tables()

def read_pickle(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)

def write_pickle(obj, fname):
    with open(fname, 'wb') as f:
        pickle.dump(obj, f)


