from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from .schema import Index

import pandas as pd
import sqlalchemy# as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
import typing
import functools
from typing import Union, Mapping, Sequence, Tuple, Set, List
from .errors import ColumnNotFoundError
#from sqlalchemy.sql import func

import warnings

class ConnectEngine:
    ''' Class to maintain sqlalchemy engine and metadata information for doctables.
    '''
    def __init__(self, target: str = None, dialect:str = 'sqlite', new_db: bool = False, 
                    foreign_keys: bool = True, echo: bool = False, 
                    **engine_kwargs):
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
        
    ######################### Dunders ######################        
    def __str__(self) -> str:
        return f'<{self.__class__.__name__}::{repr(self)}>'
    
    def __repr__(self) -> str:
        return '{}'.format(self._connstr)
        
    ######################### Core Methods ######################    
    def execute(self, query:str, *args, **kwargs) -> sqlalchemy.engine.ResultProxy:
        '''Execute query using a temporary connection.
        '''
        return self._engine.execute(query, *args, **kwargs)
        
    ######################### Inspection ######################
    def schema(self, tabname: str) -> typing.List[typing.Dict[str, typing.Any]]:
        ''' Read schema information for single table using inspect.
        Args:
            tabname: name of table to inspect.
        Returns:
            dictionary
        '''
        warnings.warn(f'.schema() is depricated. Please use '
            f'.inspect_columns() in the future.')
        
        return self.inspect_columns(tabname)
    
    def schema_df(self, tabname: str) -> pd.DataFrame:
        ''' Read schema information for table as pandas dataframe.
        Returns:
            pandas dataframe
        '''
        return pd.DataFrame(self.inspect_columns(tabname))
    
    ######################### Inspection ######################
    def inspect_columns(self, tabname: str) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Wraps Inspector.get_columns(tabname).'''
        return self.inspector.get_columns(tabname)
    
    def inspect_indices(self, tabname: str) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Wraps Inspector.get_indexes(tabname).'''
        return self.inspector.get_indexes(tabname)
        
    def inspect_columns_all(self) -> typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]]:
        '''Get column info for all tables.'''
        inspector = self.inspector
        return {tn:inspector.get_columns(tn) for tn in inspector.get_table_names()}
    
    def inspect_indices_all(self) -> typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]]:
        '''Get index info for all tables.'''
        inspector = self.inspector
        return {tn:inspector.get_indexes(tn) for tn in inspector.get_table_names()}
    
    @property
    def inspector(self) -> sqlalchemy.engine.Inspector:
        '''Get engine for this inspector.
        https://docs.sqlalchemy.org/en/14/core/reflection.html#sqlalchemy.engine.reflection.Inspector
        '''
        return sqlalchemy.inspect(self._engine)
        
    ######################### Basic Property Accessors ######################
    @property
    def dialect(self) -> str:
        return self._dialect
    
    @property
    def target(self) -> str:
        return self._target
    
    @property
    def metadata(self) -> sqlalchemy.MetaData:
        return self._metadata
        
    ######################### Access Metadata ######################
    @property
    def tables(self) -> typing.Dict[str, sqlalchemy.Table]:
        ''' Access metadata.tables
        '''
        return self._metadata.tables
    
    def list_tables(self) -> List[str]:
        ''' List table names in database connection.
        '''
        return self._engine.table_names()

    
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
        
    def remove_table(self, table: str):
        ''' Remove the given Table object from sqlalchemy metadata (not for dropping tables).
        '''
        return self._metadata.remove(table)
    
    def add_table(self, 
            tabname: str, 
            columns: List[sqlalchemy.Column] = None, 
            indices: List[Index] = None, 
            constraints: List[sqlalchemy.Constraint] = None, 
            new_table: bool = True, 
            allow_inconsistent_schema: bool = False,
            create_indices: bool = True,
            **table_kwargs
        ) -> None:
        ''' Adds a table to the metadata by name. If columns not provided, creates by autoload.
        Args:
            tabname (str): name of new table.
            columns (list/tuple): column objects passed to sqlalchemy.Table
            table_kwargs: passed to sqlalchemy.Table constructor.
        '''
        table_kwargs = dict(table_kwargs)

        inspector = self.inspector

        # a schema was provided
        if columns is not None: 
            
            # metadata was found, so using that
            if tabname in self._engine.table_names():
                exist_cn = set(c.name for c in self.tables[tabname].columns)
                if not allow_inconsistent_schema:
                    self.check_column_consistency(exist_cn, columns)
                
                #table_kwargs['keep_existing'] = False
                table_kwargs['extend_existing'] = True
                table = self.new_table(tabname, columns, **table_kwargs)
            
            # we have no metadata but the table does exist
            elif tabname in inspector.get_table_names():
                exist_cn = set(c['name'] for c in inspector.get_columns(tabname))
                if not allow_inconsistent_schema:
                    self.check_column_consistency(exist_cn, columns)

                table = self.new_table(tabname, columns, **table_kwargs)
            
            # table does not exist and no metadata is present
            else:
                if new_table:
                    table = self.new_table(tabname, columns, **table_kwargs)
                    table.create(self._engine)
                else:
                    raise sqlalchemy.exc.ProgrammingError('"new_table" '
                        f'was set to false but table does not exist yet.')

        # infer schema from existing table
        else: 
            try:
                #https://docs.sqlalchemy.org/en/14/core/metadata.html#sqlalchemy.schema.Table.params.autoload_with
                table = self.reflect_table(tabname, **table_kwargs)
            except sqlalchemy.exc.NoSuchTableError as e:
                tables = self.list_tables()
                raise sqlalchemy.exc.NoSuchTableError(f'Couldn\'t find table {tabname}! Existing tables: {tables}!') from e
                
        
        if create_indices and indices is not None:
            self.create_indices(indices, table, allow_inconsistent_schema)
                
        if constraints is not None:
            const_info = (
                inspector.get_check_constraints(tabname) +
                inspector.get_foreign_keys(tabname) +
                inspector.get_unique_constraints(tabname)
            )
            exist_const = set(const['name'] for const in const_info)

            for constraint in constraints:
                if constraint.name not in exist_const:
                    constraint.name # NOTE: DO THIS!!!!
        
        # Binds .max(), .min(), .count(), .sum() to each column object.
        # https://docs.sqlalchemy.org/en/13/core/functions.html
        
        for col in table.c:
            col.max = functools.partial(sqlalchemy.sql.func.max, col)
            col.min = functools.partial(sqlalchemy.sql.func.min, col)
            col.count = functools.partial(sqlalchemy.sql.func.count, col)
            col.sum = functools.partial(sqlalchemy.sql.func.sum, col)

            def func_custom(attr: str):
                '''Allows user to specify any sqlalchemy function name.'''
                return getattr(sqlalchemy.sql.func, attr)(col)
            col.func = func_custom
        
        return table

    def new_table(self,
            tabname, 
            columns: typing.List[sqlalchemy.Column],
            #indices: typing.List[sqlalchemy.Index],
            #constraints: typing.List[sqlalchemy.Constraint],
            **table_kwargs: typing.Dict[str, typing.Any],
        ) -> sqlalchemy.Table:
        return sqlalchemy.Table(tabname, self._metadata, 
            *columns, 
            **table_kwargs,
        )

    def reflect_table(self,
            tabname, 
            **table_kwargs: typing.Dict[str, typing.Any],
        ) -> sqlalchemy.Table:
        return sqlalchemy.Table(
            tabname, 
            self._metadata, 
            #autoload=True, # depricated: now uses autoload_with
            autoload_with=self._engine, 
            **table_kwargs
        )

    def create_indices(self, 
            indices: typing.List[Index], 
            table: sqlalchemy.Table, 
            allow_inconsistent_schema: bool
        ) -> None:
        
        new_indices = self.get_new_indices(table.name, indices, allow_inconsistent_schema)
        
        # used to convert strings to actual column objects
        col_lookup = {c.name:c for c in table.columns}
        
        for ind in new_indices:
            try:
                sa_ind = ind.get_sqlalchemy_index(col_lookup)
            except KeyError as e:
                violators = {c for c in ind.columns if c not in col_lookup}
                raise ColumnNotFoundError(f'The following index-associated columns were not found in '
                    f'table "{table.name}": {violators}. Use create_indices=False to ignore '
                    f'the creation of this index.')

            # this will actually create the engine
            sa_ind.create(self._engine)
    
    @staticmethod
    def check_column_consistency(
            existing_colnames: typing.Set[str], 
            provided_cols: typing.Set[sqlalchemy.Column],
        ):
        provided_colnames = set(c.name for c in provided_cols)
        if existing_colnames != provided_colnames:
            raise ValueError(f'Provided schema columns do not match existing '
                f'db table names. {existing_colnames=}, {provided_colnames=} '
                f'use allow_consistent_schema=True to ignore this error.')

    def get_new_indices(self,
            tabname: str,
            indices: typing.List[Index],
            allow_inconsistent_schema: bool,
        ) -> typing.List[Index]:
        inspector = self.inspector
        exist_ind = {ind['name']:tn for tn in inspector.get_table_names() 
                        for ind in inspector.get_indexes(tn)}
                
        # make sure existing indices with the same name are associated with same table
        a = any(exist_ind[ind.name] != tabname for ind in indices if ind.name in exist_ind)
        if not allow_inconsistent_schema and a:
            violators = {ind.name: exist_ind[ind.name] for ind in indices 
                if exist_ind.get(ind.name,tabname) != tabname}
            raise ValueError(f'The following indices have already been '
                f'assigned to another table: {violators=}. Set '
                f'create_indices=False or allow_inconsistent_schema=True '
                f'to ignore this error.')
        
        return [ind for ind in indices if ind.name not in exist_ind]
    
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







