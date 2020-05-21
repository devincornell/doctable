
import sqlalchemy as sa

class ConnectEngine:
    engine = None
    target = None
    engine_args = None
    metadata = None
    tables = None
    
    def __init__(self, engine, target, **engine_args):
        
        # create sqlalchemy engine
        self.connstr = '{}:///{}'.format(engine_type, fname)
        self.engine = sa.create_engine(connstr, **engine_args)
        
        # start working with the sqlalchemy metadata
        metadata = sa.MetaData()
    
    def add_schema():
        
if __name__ == '__main__':
    
    
    
    