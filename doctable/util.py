
import sqlalchemy as sa

def list_tables(fname, engine='sqlite', **engine_args):
    ''' List tables in an sqlite database.
    Args:
        engine (str): sql engine to use for conenction
        engine_args (kwargs): passed to sqlalchemy create_engine
    '''
    connstr = '{}:///{}'.format(engine,fname)
    engine = sa.create_engine(connstr, **engine_args)
    return engine.table_names()

