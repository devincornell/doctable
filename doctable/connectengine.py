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
            
        # store for convenience
        self._dialect = dialect
        self._target = target
        self._connstr = '{}:///{}'.format(self._dialect, self._target)
        
        # create sqlalchemy engine
        #self._engine_kwargs = engine_kwargs
        self._engine = sqlalchemy.create_engine(self._connstr, echo=self._echo, **engine_kwargs)
        self._metadata = sqlalchemy.MetaData(bind=self._engine)
        
        
    def __del__(self):
        # used instead of garbage collector to reliably kill connections
        self._engine.dispose()
        
    ######################### Core Methods ######################    
    def execute(self, query, **kwargs):
        ''' Open temporary connection and execute query.
        '''
        #with self.get_connection() as conn:
        #    r = conn.execute(query)
        return self._engine.execute(query, **kwargs)
        
    ######################### Convenient Properties ######################
    @property
    def dialect(self):
        return self._dialect
    
    @property
    def target(self):
        return self._target
    
    def __str__(self):
        return '<ConnectEngine{}>'.format(repr(self))
    
    def __repr__(self):
        return '{}'.format(self._connstr)
    
    ######################### Engine and Connection Management ######################
    
    def get_connection(self):
        ''' Open new connection in engine connection pool.
        '''
        return self._engine.connect()
    
    def reopen(self):
        ''' Deletes all connections and clears metadata.
        '''
        self.close_connections()
        self.clear_metadata()
    
    def close_connections(self):
        ''' Closes all existing connections attached to engine.
        '''
        return self._engine.dispose()
    
    def clear_metadata(self):
        for table in self._metadata.sorted_tables:
            self.remove_table(table)
    
    ######################### Table Management ######################
    
    def list_tables(self):
        ''' List table names in database connection.
        '''
        return self._engine.table_names()
    
    @property
    def tables(self):
        ''' Get table objects stored in metadata.
        '''
        return self._metadata.tables
    
    def schema(self, tabname):
        ''' Read schema information for single table.
        Returns:
            dictionary
        '''
        inspector = sqlalchemy.inspect(self._engine)
        return inspector.get_columns(tabname)
    
    def schema_table(self, tabname):
        ''' Read schema information for table as pandas dataframe.
        Returns:
            pandas dataframe
        '''
        return pd.DataFrame(self.schema(tabname))
    
    def add_table(self, tabname, columns=None, **kwargs):
        ''' Adds a table to the metadata. If columns not provided, creates by autoload.
        Args:
            tabname (str): name of new table.
            columns (list/tuple): column objects passed to sqlalchemy.Table
            kwargs: passed to sqlalchemy.Table constructor.
        '''
        if tabname in self.tables:
            return self.tables[tabname]
        
        if columns is not None:
            table = sqlalchemy.Table(tabname, self._metadata, *columns, **kwargs)
            table.create(self._engine)
            #self._metadata.create_all(self._engine) # create table if it doesn't exist
        else:
            try:
                table = sqlalchemy.Table(tabname, self._metadata, autoload=True, autoload_with=self._engine, **kwargs)
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
    
    def drop_table(self, table, if_exists=False, **kwargs):
        ''' Drops table, either sqlalchemy object or by executing DROP TABLE.
        Args:
            table (sqlalchemy.Table/str): table object or name to drop.
            if_exists (bool): if true, won't throw exception if table doesn't exist.
        '''
        if isinstance(table, sqlalchemy.Table):
            return table.drop(self._engine, checkfirst=if_exists, **kwargs)
        
        else:
            if if_exists:
                return self.execute(f'DROP TABLE IF EXISTS {tabname}', **kwargs)
            else:
                return self.execute(f'DROP TABLE {tabname}', **kwargs)
    
    def remove_table(self, table):
        ''' Remove the given Table object from MetaData object. Does not drop.
        '''
        return self._metadata.remove(table)
            

    

    

        
        
