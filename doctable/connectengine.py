import pandas as pd
import sqlalchemy# as sa
import os
from datetime import datetime
#from sqlalchemy.sql import func

class ConnectEngine:
    engine = None
    metadata = None
    dialect = None
    target = None
    engine_kwargs = None
    
    def __init__(self, target=None, dialect='sqlite', new_db=False, foreign_keys=False,
                 timeout=None, echo=False, **engine_kwargs):
        ''' Initializes sqlalchemy engine object.
            Args:
                target: choose target database for connection.
                echo: sets the echo status used in sqlalchemy.create_engine().
                    This will output every sql query upon execution.
                engine_kwargs: passed directly to sqlalchemy.create_engine().
                    See more options in the official docs:
                    https://docs.sqlalchemy.org/en/13/core/engines.html#sqlalchemy.create_engine
        '''
        
        if dialect.startswith('sqlite'):
            if target != ':memory:': #not creating in-memory database
                exists = os.path.exists(target)
                if not new_db and not exists:
                    raise FileNotFoundError('new_db is set to False but the database {} does not '
                                     'exist yet.'.format(target))

            if timeout is not None:
                engine_kwargs = {**engine_kwargs, 'timeout':timeout}

        
        self._echo = echo
        self._foreign_keys = foreign_keys
            
        # store connection info
        self._dialect = dialect
        self._target = target
        
        # create sqlalchemy engine
        self._engine_kwargs = engine_kwargs
        self.open()
        
    @property
    def _connstr(self):
        return '{}:///{}'.format(self._dialect, self._target)
    
    def __str__(self):
        return '<ConnectEngine{}>'.format(repr(self))
    
    def __repr__(self):
        openstr = 'open' if self.is_open() else 'closed'
        return '[{}]::{}'.format(openstr, self._connstr)
    
    def get_connection(self):
        ''' Open new connection in engine connection pool.
        '''
        return self._engine.connect()
        
    def open(self):
        ''' Open the engine and bind metadata.
        '''
        self._engine = sqlalchemy.create_engine(self._connstr, echo=self._echo, **self._engine_kwargs)
        self._metadata = sqlalchemy.MetaData(bind=self._engine)
        if self._foreign_keys:
            self.execute('PRAGMA foreign_keys=ON')
        
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
            try:
                table = sqlalchemy.Table(tabname, self._metadata, autoload=True, autoload_with=self._engine)
            except sqlalchemy.exc.NoSuchTableError:
                tables = self.list_tables()
                raise sqlalchemy.exc.NoSuchTableError(f'Couldn\'t find table {tabname}! Existing tables: {tables}!')
        
        # Binds .max(), .min(), .count(), .sum() to each column object.
        # https://docs.sqlalchemy.org/en/13/core/functions.html
        for col in table.c:
            col.max = sqlalchemy.sql.func.max(col)
            col.min = sqlalchemy.sql.func.min(col)
            col.count = sqlalchemy.sql.func.count(col)
            col.sum = sqlalchemy.sql.func.sum(col)
        
        return table
    
    def drop_table(self, tabname, if_exists=False):
        ''' Executes DROP TABLE query.
        '''
        if if_exists:
            self.execute(f'DROP TABLE IF EXISTS {tabname}')
        else:
            self.execute(f'DROP TABLE {tabname}')
            
    def schema(self, tabname):
        ''' Read schema information.
        Returns:
            dictionary
        '''
        inspector = sqlalchemy.inspect(self._engine)
        return inspector.get_columns(tabname)
    
    def schema_table(self, tabname):
        ''' Read schema information as pandas dataframe.
        Returns:
            pandas dataframe
        '''
        return pd.DataFrame(self.schema(tabname))
    
    def list_tables(self):
        ''' List tables in database connection.
        '''
        return self._engine.table_names()
    
    def execute(self, query):
        ''' Open temporary connection and execute query.
        '''
        with self.get_connection() as conn:
            r = conn.execute(query)
        
        
