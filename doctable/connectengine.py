import pandas as pd
import sqlalchemy# as sa
import os
#from sqlalchemy.sql import func

class ConnectEngine:
    engine = None
    metadata = None
    dialect = None
    target = None
    engine_kwargs = None
    
    def __init__(self, dialect='sqlite', target=':memory:', new_db=False, 
                 **engine_kwargs):
        
        if not new_db and dialect=='sqlite' and not (target==':memory:' or os.path.exists(fname)):
            raise FileNotFoundError('new_db is set to False but the database does not '
                             'exist yet.')
            
        # store connection info
        self.dialect = dialect
        self.target = target
        
        # create sqlalchemy engine
        self.connstr = '{}:///{}'.format(dialect, target)
        self.engine_kwargs = engine_kwargs
        self.open()
    
    def get_connection(self):
        return self.engine.connect()
        
    def open(self):
        self.engine = sqlalchemy.create_engine(self.connstr, **self.engine_kwargs)
        self.metadata = sqlalchemy.MetaData()
        
    def close(self):
        self.engine = None
        self.metadata = None
        
    def is_open(self):
        return self.engine is not None
    
    def add_table(self, tabname, columns=None):
        if columns is not None:
            table = sqlalchemy.Table(tabname, self.metadata, *columns)
            self.metadata.create_all(self.engine) # create table if it doesn't exist
        else:
            table = sqlalchemy.Table(tabname, self.metadata, autoload=True, autoload_with=self.engine)
        
        # Binds .max(), .min(), .count(), .sum() to each column object.
        # https://docs.sqlalchemy.org/en/13/core/functions.html
        for col in table.c:
            col.max = sqlalchemy.sql.func.max(col)
            col.min = sqlalchemy.sql.func.min(col)
            col.count = sqlalchemy.sql.func.count(col)
            col.sum = sqlalchemy.sql.func.sum(col)
        
        return table
            
    def schema(self, tabname):
        inspector = sqlalchemy.inspect(self.engine)
        return inspector.get_columns(tabname)
    
    def schema_table(self, tabname):
        return pd.DataFrame(self.schema(tabname))
    
    def list_tables(self):
        return self.engine.table_names()
        
        
