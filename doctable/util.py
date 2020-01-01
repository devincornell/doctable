


def list_tables(fname, engine='sqlite', **engine_args):
    
    connstr = '{}:///{}'.format(engine,fname)
    engine = sa.create_engine(connstr, **engine_args)
    return engine.table_names()

