import pandas as pd
import sqlalchemy# as sa
import os
from datetime import datetime
import typing
from typing import Union, Mapping, Sequence, Tuple, Set, List
#from sqlalchemy.sql import func

class ConnectEngine:
    ''' Class to maintain sqlalchemy engine and metadata information for doctables.
    '''
    def __init__(self, target: str = None, dialect:str = 'sqlite', new_db: bool = False, 
                    foreign_keys: bool = False, timeout: int = None, echo: bool = False, 
                    **engine_kwargs):
        ''' Initializes sqlalchemy engine  and metadata objects.
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
        
        if self._foreign_keys:
            self.execute('pragma foreign_keys=ON')
        
        
    def __del__(self):
        try:
            # used instead of garbage collector to reliably kill connections
            self._engine.dispose()
        except:# AttributeError:
            pass
        
    ######################### Core Methods ######################    
    def execute(self, query:str, **kwargs) -> sqlalchemy.engine.ResultProxy:
        ''' Open temporary connection and execute query.
        '''
        #with self.get_connection() as conn:
        #    r = conn.execute(query)
        return self._engine.execute(query, **kwargs)
        
    ######################### Convenient Properties ######################
    @property
    def dialect(self) -> str:
        return self._dialect
    
    @property
    def target(self) -> str:
        return self._target
    
    def list_tables(self) -> List[str]:
        ''' List table names in database connection.
        '''
        return self._engine.table_names()
    
    @property
    def tables(self) -> List[sqlalchemy.Table]:
        ''' Get table objects stored in metadata.
        '''
        return self._metadata.tables
    
    def __str__(self) -> str:
        return '<ConnectEngine::{}>'.format(repr(self))
    
    def __repr__(self) -> str:
        return '{}'.format(self._connstr)
    
    ######################### Engine and Connection Management ######################
    
    def get_connection(self) -> sqlalchemy.engine.Connection:
        ''' Open new connection in engine connection pool.
        '''
        return self._engine.connect()
    
    def reopen(self) -> sqlalchemy.engine.ResultProxy:
        ''' Deletes all connections and clears metadata.
        '''
        self.close_connections()
        self.clear_metadata()
        
        # not sure if this needs to be here, but can't hurt
        if self._foreign_keys:
            return self.execute('pragma foreign_keys=ON')
    
    def close_connections(self) -> sqlalchemy.engine.ResultProxy:
        ''' Closes all existing connections attached to engine.
        '''
        return self._engine.dispose()
    
    def clear_metadata(self) -> None:
        for table in self._metadata.sorted_tables:
            self.remove_table(table)
    
    
    ######################### Table Management ######################
    
    def schema(self, tabname: str) -> Sequence[sqlalchemy.Column]:
        ''' Read schema information for single table.
        Returns:
            dictionary
        '''
        inspector = sqlalchemy.inspect(self._engine)
        return inspector.get_columns(tabname)
    
    def schema_df(self, tabname: str) -> pd.DataFrame:
        ''' Read schema information for table as pandas dataframe.
        Returns:
            pandas dataframe
        '''
        return pd.DataFrame(self.schema(tabname))
    
    def remove_table(self, table: str):
        ''' Remove the given Table object from MetaData object. Does not drop.
        '''
        return self._metadata.remove(table)
    
    def add_table(self, tabname: str, columns: Sequence[typing.Sequence] = None, 
                    new_table: bool = True, **table_kwargs) -> None:
        ''' Adds a table to the metadata. If columns not provided, creates by autoload.
        Args:
            tabname (str): name of new table.
            columns (list/tuple): column objects passed to sqlalchemy.Table
            table_kwargs: passed to sqlalchemy.Table constructor.
        '''
        # return table instance if already stored in metadata object
        if tabname in self._metadata.tables:
            return self.tables[tabname]
        
        # create new table with provided columns
        if columns is not None:
            table = sqlalchemy.Table(tabname, self._metadata, *columns, **table_kwargs)
            if tabname not in self._engine.table_names():
                if new_table:
                    table.create(self._engine)
                else:
                    raise sqlalchemy.ProgrammingError('"new_table" was set to false but table '
                                                     'does not exist yet.')
                
            #self._metadata.create_all(self._engine) # create table if it doesn't exist
        
        else: # infer schema from existing table
            try:
                table = sqlalchemy.Table(tabname, self._metadata, autoload=True, autoload_with=self._engine, **table_kwargs)
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
    
    
    def add_existing_tables(self, **table_kwargs) -> None:
        ''' Will register all existing tables in metadata.
        '''
        for tabname in self.list_tables():
            self.add_table(tabname, **table_kwargs)
    
    
    def drop_table(self, table: Union[sqlalchemy.Table, str], if_exists: bool = False, 
                    **kwargs) -> None:
        ''' Drops table, either sqlalchemy object or by executing DROP TABLE.
        Args:
            table (sqlalchemy.Table/str): table object or name to drop.
            if_exists (bool): if true, won't throw exception if table doesn't exist.
        '''
        if isinstance(table, sqlalchemy.Table):
            return table.drop(self._engine, checkfirst=if_exists, **kwargs)
        
        else: # table is a string
            if table not in self._metadata.tables:
                self.add_table(table)
            return self._metadata.tables[table].drop(self._engine, checkfirst=if_exists, **kwargs)
    
            

    

    

        
        
