import pandas as pd
import sqlalchemy# as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import typing
from typing import Union, Mapping, Sequence, Tuple, Set, List
#from sqlalchemy.sql import func

class ConnectEngine:
    ''' Class to maintain sqlalchemy engine and metadata information for doctables.
    '''
    def __init__(self, target: str = None, dialect:str = 'sqlite', new_db: bool = False, 
                    foreign_keys: bool = True, echo: bool = False, 
                    orm: bool = False, engine_kwargs={}, **connect_args):
        ''' Initializes sqlalchemy engine  and metadata objects.
            Args:
                target: choose target database for connection.
                echo: sets the echo status used in sqlalchemy.create_engine().
                    This will output every sql query upon execution.
                connect_args: passed to sqlalchemy.create_engine() as the connect_args param.
                    See more options in the official docs:
                    https://docs.sqlalchemy.org/en/13/core/engines.html#sqlalchemy.create_engine
        '''
        
        if dialect.startswith('sqlite'):
            if target != ':memory:': #not creating in-memory database
                exists = os.path.exists(target)
                if not new_db and not exists:
                    raise FileNotFoundError('new_db is set to False but the database {} does not '
                                     'exist yet.'.format(target))

            #if timeout is not None:
            #    connect_args = {**connect_args, 'timeout':timeout}

        
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

        # add other tables that exist in the database already
        self.reflect()
        
    def __del__(self):
        # I seriously don't understand why the hell this isn't needed...
        # solved some major issues by removing though
        #if hasattr(self, '_engine'):
        #    self._engine.dispose()
        #    self._engine = None
        pass
        
    ######################### Core Methods ######################    
    def execute(self, query:str, **kwargs) -> sqlalchemy.engine.ResultProxy:
        '''Execute query using a temporary connection.
        '''
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
        ''' Access metadata.tables
        '''
        return self._metadata.tables
    
    def get_session(self):
        '''TODO: this function is not implemented.'''
        raise NotImplementedError
        #return self.Session()
    
    def __str__(self) -> str:
        return f'<{self.__class__.__name__}::{repr(self)}>'
    
    def __repr__(self) -> str:
        return '{}'.format(self._connstr)
    
    ######################### Engine and Connection Management ######################
    
    def connect(self) -> sqlalchemy.engine.Connection:
        ''' Open new connection in the engine connection pool.
        '''
        return self._engine.connect()
    
    def reopen(self) -> sqlalchemy.engine.ResultProxy:
        ''' Deletes all connections and clears metadata.
        '''
        self.dispose()
        self.clear_metadata()
        
        # not sure if this needs to be here, but can't hurt
        if self._foreign_keys:
            return self.execute('pragma foreign_keys=ON')
    
    def dispose(self) -> sqlalchemy.engine.ResultProxy:
        ''' Closes all existing connections attached to engine.
        '''
        if hasattr(self, '_engine'):
            return self._engine.dispose()
        else:
            return None
    
    def clear_metadata(self) -> None:
        '''Remove all tables from sqlalchemy metadata.
        '''
        for table in self._metadata.sorted_tables:
            self.remove_table(table)
    
    
    ######################### Table Management ######################
    def create_all(self):
        ''' Create table metadata from all existing tables.
        '''
        return self._metadata.create_all(self._engine)
    
    def schema(self, tabname: str) -> Sequence[sqlalchemy.Column]:
        ''' Read schema information for single table using inspect.
        Args:
            tabname: name of table to inspect.
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
        ''' Remove the given Table object from sqlalchemy metadata.
        '''
        return self._metadata.remove(table)
    
    def add_table(self, tabname: str, columns: Sequence[typing.Sequence] = None, 
                    new_table: bool = True, **table_kwargs) -> None:
        ''' Adds a table to the metadata by name. If columns not provided, creates by autoload.
        Args:
            tabname (str): name of new table.
            columns (list/tuple): column objects passed to sqlalchemy.Table
            table_kwargs: passed to sqlalchemy.Table constructor.
        '''

        # remove table if it is already in metadata, then replace it
        if tabname in self._metadata.tables:
            #self.remove_table(self.tables[tabname])
            table_kwargs['extend_existing'] = True
        
        # create new table with provided columns
        if columns is not None:
            try:
                table = sqlalchemy.Table(tabname, self._metadata, *columns, **table_kwargs)
            except: # make error more transparent
                raise ValueError(f'Error creating table. Data provided: {tabname}, '
                    f'metadata={self._metadata}, columns={columns}, table_kwargs={table_kwargs}')
            if tabname not in self._engine.table_names():
                if new_table:
                    table.create(self._engine)
                else:
                    raise sqlalchemy.exc.ProgrammingError('"new_table" was set to false but table '
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
    
    
    def reflect(self, **kwargs) -> None:
        ''' Will register all existing tables using metadata.reflect().
        '''
        #for tabname in self.list_tables():
        #    self.add_table(tabname, **kwargs)
        return self._metadata.reflect(**kwargs)
    
    
    def drop_table(self, table: Union[sqlalchemy.Table, str], if_exists: bool = False, 
                    **kwargs) -> None:
        '''Drops table, either sqlalchemy object or by executing DROP TABLE.
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
    
            

    

    

        
        
