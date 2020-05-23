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
    
    def __init__(self, dialect='sqlite', target=':memory:', new_db=False, foreign_keys=False,
                 timeout=None, **engine_kwargs):
        
        if dialect.startswith('sqlite') and target != ':memory:':
            exists = os.path.exists(target)
            if not new_db and not exists:
                raise FileNotFoundError('new_db is set to False but the database does not '
                                 'exist yet.')
        
        if dialect.startswith('sqlite') and timeout is not None:
            engine_kwargs = {**engine_kwargs, 'timeout':timeout}
            
        # store connection info
        self._dialect = dialect
        self._target = target
        
        # create sqlalchemy engine
        self._connstr = '{}:///{}'.format(dialect, target)
        self._engine_kwargs = engine_kwargs
        self.open()
        
        if foreign_keys:
            self.execute('PRAGMA foreign_keys=ON')
        
    
    def get_connection(self):
        return self._engine.connect()
        
    def open(self):
        self._engine = sqlalchemy.create_engine(self._connstr, **self._engine_kwargs)
        self._metadata = sqlalchemy.MetaData()
        
    def close(self):
        self._engine = None
        self._metadata = None
        
    def is_open(self):
        return self._engine is not None
    
    def add_table(self, tabname, columns=None):
        if columns is not None:
            table = sqlalchemy.Table(tabname, self._metadata, *columns)
            self._metadata.create_all(self._engine) # create table if it doesn't exist
        else:
            table = sqlalchemy.Table(tabname, self._metadata, autoload=True, autoload_with=self._engine)
        
        # Binds .max(), .min(), .count(), .sum() to each column object.
        # https://docs.sqlalchemy.org/en/13/core/functions.html
        for col in table.c:
            col.max = sqlalchemy.sql.func.max(col)
            col.min = sqlalchemy.sql.func.min(col)
            col.count = sqlalchemy.sql.func.count(col)
            col.sum = sqlalchemy.sql.func.sum(col)
        
        return table
            
    def schema(self, tabname):
        inspector = sqlalchemy.inspect(self._engine)
        return inspector.get_columns(tabname)
    
    def schema_table(self, tabname):
        return pd.DataFrame(self.schema(tabname))
    
    def list_tables(self):
        return self._engine.table_names()
    
    def execute(self, query):
        with self.get_connection() as conn:
            r = conn.execute(query)
        
        
