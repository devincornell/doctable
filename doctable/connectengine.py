
import sqlalchemy as sa


class ConnectEngine:
    engine = None
    metadata = None
    engine_type = None
    target = None
    engine_kwargs = None
    
    def __init__(self, engine_type='sqlite', target=':memory:', **engine_kwargs):
        
        # store connection info
        self.engine_type = engine_type
        self.target = target
        
        # create sqlalchemy engine
        self.connstr = '{}:///{}'.format(engine_type, target)
        self.engine_kwargs = engine_kwargs
        self.open()
    
    def get_connection(self):
        return self.engine.connect()
        
    def open(self):
        self.engine = sa.create_engine(self.connstr, **self.engine_kwargs)
        self.metadata = sa.MetaData()
        
    def close(self):
        self.engine = None
        self.metadata = None
        
    def is_open(self):
        return self.engine is not None
    
    def add_table(self, tabname, columns=None):
        if columns is not None:
            table = sa.Table(tabname, self.metadata, *columns)
            self.metadata.create_all(self.engine) # create table if it doesn't exist
        else:
            table = sa.Table(tabname, self.metadata, autoload=True, autoload_with=self.engine)
        return table
            
        

    
    