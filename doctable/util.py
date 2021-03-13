

import pickle
from multiprocessing import Pool

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



def malloc_thread(i, k=10000000):
    stuff = list()
    while True:
        try:
            stuff.append(list(range(k)))
        except:
            print('.', end='')

def showstopper(n_cores=12, n=100000):
    with Pool(n_cores) as p:
        p.map(malloc_thread, list(range(n)))