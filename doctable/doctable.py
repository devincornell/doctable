from __future__ import annotations

import collections
from time import time
import pprint
import random
import pandas as pd
import os
import copy
from glob import glob
from datetime import datetime
import typing
from typing import Union, Mapping, Sequence, Tuple, Set, List
import dataclasses
import warnings
#from .schema import SchemaObject, DocTableSchema
from doctable.util import QueueInserter

# operators like and_, or_, and not_, functions like sum, min, max, etc
#import sqlalchemy as sa
import sqlalchemy

from .util import is_sequence, parse_static_arg
from .schema import SchemaObject, FileTypeBase, DocTableSchema, Constraint, Index
from .models import DocBootstrap
#from .util import list_tables
from .connectengine import ConnectEngine
from .query import Query
from .schema import (
    StringSchema, 
    DataclassSchema, 
    InferredSchema, 
    RowDictSchema,
    RowToObjectConversionFailedError, 
    has_attr_map, 
    has_rowdict,
)

DEFAULT_TABNAME = '_documents_'

class DocTable:
    ''' Class for managing a single database table.
    Description: This class manages schema and connection information to provide
        an object-based interface to perform queries on a single table 
        in a database (although multi-table designs are possible with 
        multiple DocTables). It is designed to maintain informabout about the 
        underlying database structure of the table, making it possible to 
        execute queries without using the SQL language.

    Settable static attributes (overridden if related constructor argument passed):
        _target_ (str): target database to connect to - used when a doctable
            will always connect to the same target (i.e., a server etc).
        _tabname_ (str): name of table to connect to (and create).
        _schema_ (DocTableSchema): schema definition for this doctable, to be used
            when creating a new table and to manage table information.
        _indices_ (dict): indices to apply to the table
        _constraints_ (list): constraints to apply to the table
        _doctable_args_ (dict): any other constructor arguments that should always
            be used when instantiating. Overridden by providing arguments
            to the constructor.
    '''
    def __init__(self, 
            target: str = None, schema: DocTableSchema = None, tabname: str = None, 
            indices: typing.List[Index] = None, constraints: typing.List[Constraint] = None,
            dialect: str = 'sqlite', engine: ConnectEngine = None, 
            readonly: bool = False, new_db: bool = False, new_table: bool = True, 
            persistent_conn: bool = False, verbose: bool = False, 
            allow_inconsistent_schema: bool = False, create_indices: bool = True,
            **engine_kwargs):
        '''Create new database.
        Args:
            target (str): filename for database to connect to. ":memory:" is a 
                special value indicating to the python sqlite engine that the db
                should be created in memory. Will create new empty database file
                if it does not exist and new_db==True, and add a new table using
                specified schema if new_table==True.
            tabname (str): table name for this specific doctable.
            schema (type or list<list>): schema from which to create db. Includes a
                list of column names and types (including contraints and indexes) as tuples
                defined according to information needed to construct the sqlalchemy
                objects. Alternatively, can be a schema class (see docs).
            dialect (str): database engine through which to construct db.
                For more info, see sqlalchemy dialect info:
                https://docs.sqlalchemy.org/en/13/dialects/
            engine (ConnectEngine): engine from another doctable if working with different
                tables in the same db.
            readonly (bool): Prevents user from calling insert(), delete(), or 
                update(). Will not block other sql possible commands.
            new_db (bool): Indicate if new db file should be created given 
                that a schema is provided and the db file doesn't exist.
            new_table (bool): Allow doctable to create a new table if one 
                doesn't exist already.
            persistent_conn (bool): whether or not to create a persistent conn 
                to database. Otherwise will create temporary connection for each
                query.
            verbose (bool): Print every sql command before executing.
            engine_kwargs (**kwargs): Pass directly to the sqlalchemy
                .create_engine() as connect_args. Args typically vary by dialect.
                Example: connect_args={'timeout': 15} for sqlite
                or connect_args={'connect_timeout': 15} for PostgreSQL.

        '''
        # handle defaults
        tabname = parse_static_arg(self, tabname, 'tabname', '_tabname_', DEFAULT_TABNAME)
        schema = parse_static_arg(self, schema, 'tabname', '_schema_', None)
        target = parse_static_arg(self, target, 'tabname', '_target_', None)

        # dependent args
        if readonly:
            new_db = False
            new_table = False

        # if no engine or schema is provided, the database must already exist and user intends to infer
        if dialect.startswith('sqlite'):
            if schema is None and engine is None and (target == ':memory:' or not os.path.exists(target)):
                raise ValueError('Schema must be provided if using memory database or '
                             'database file does not exist yet. Need to provide schema '
                             'when creating a new table.')

        # set target and engine
        if target is None:
            try:
                target = engine.target
            except AttributeError as e:
                raise ValueError(f'Either target or engine must be provided.') from e
        
            self._engine = engine

        elif engine is None:
            self._engine = ConnectEngine(
                target = target, 
                dialect = dialect, 
                new_db = new_db, 
                **engine_kwargs
            )
        else:
            raise ValueError(f'Cannot provide both target and engine.')
        
        # store arguments as-is
        self._tabname = tabname
        self._target = target
        self.dialect = dialect
        self._new_db = new_db

        # flags
        self.verbose = verbose
        self.persistent_conn = persistent_conn
        self.readonly = readonly
        self._new_table = new_table
                
        # connect to existing table or create new one
        # NOTE: this is not a good way to detect the schema type - make something more obvious
        if hasattr(schema, '_doctable_from_row_obj'):
            self._schema = RowDictSchema.from_schema_definition(
                schema_class = schema,
                indices = indices, # need these if we want to grab from constructor
                constraints = constraints,
            )
        elif has_attr_map(schema):
            self._schema = DataclassSchema.from_schema_definition(
                schema_class = schema,
                indices = indices, # need these if we want to grab from constructor
                constraints = constraints,
            )
        elif is_sequence(schema):
            self._schema = StringSchema.from_schema_definition(
                schema_list = schema,
                default_fpath = self._target+'_'+self._tabname,
            )
        else:
            #self._schema = None # inferred from existing table
            self._schema = InferredSchema.from_schema_definition(schema)

        # add this table
        self._table = self._engine.add_table(
            tabname = self._tabname, 
            columns = self._schema.columns, 
            indices = self._schema.indices,
            constraints = self._schema.constraints,
            new_table=self._new_table,
            allow_inconsistent_schema = allow_inconsistent_schema,
            create_indices = create_indices,
        )
        
        # create persistent connection to database if requested
        self._conn = self._engine.connect() if self.persistent_conn else None
        
    def __del__(self):
        ''' Closes database connection to prevent locking db.
        '''
        # apparently engines and connections are garbage collected using event handlers?
        # I don't understand this, but solved some big issues by just doing nothing.
        
        #self._engine.remove_table(self._table) # remove from engine metadata
        #self.close_conn()
        pass

        
    
    #################### Connection Methods ###################

    def __enter__(self):
        '''Calls .open_conn()
        '''
        self.open_conn()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        '''Calls .close_conn()
        '''
        return self.close_conn()
    
    def close_conn(self) -> None:
        ''' Closes connection to db (if one exists). '''
        if self._conn is not None:
            self._conn.close()
            self._conn = None
    
    def open_conn(self) -> None:
        ''' Opens connection to db (if one does not exist). '''
        
        if self._conn is None:
            self._conn = self._engine.connect()
            
    def connect(self) -> sqlalchemy.engine.Connection:
        '''Returns a connection from the sqlalchemy engine.'''
        return self._engine.connect()
    
    def reopen_engine(self, open_conn=None) -> None:
        ''' Opens connection engine. 
        Args:
            open_conn (bool): create a new db connection.
        '''
        self.close_conn()
        self._engine.reopen()
        if open_conn or (open_conn is None and self.persistent_conn):
            self.open_conn()


    #################### Dunder ###################
    
    def __str__(self) -> str:
        return f'<{self.__class__.__name__} ({len(self.columns)} cols)::{repr(self._engine)}:{self._tabname}>'
    
    
    
    #################### Expose Underlying Table ###################
    def __getitem__(self, colname) -> sqlalchemy.Column:
        '''Accesses a column object by calling .col().'''
        return self.col(colname)
    
    def col(self,name) -> sqlalchemy.Column:
        '''Accesses a column object.
        Args:
            Name of column to access. Applied as subscript to 
                sqlalchemy columns object.
        '''
        if isinstance(name, sqlalchemy.Column):
            return name
        return self._table.c[name]
        
    @property
    def table(self) -> sqlalchemy.Table:
        '''Returns underlying sqlalchemy table object for manual manipulation.
        '''
        return self._table
    
    @property
    def tabname(self) -> str:
        '''Gets name of table for this connection.'''
        return self._tabname
    
    @property
    def columns(self) -> sqlalchemy.sql.base.ImmutableColumnCollection:
        '''Exposes SQLAlchemy core table columns object.
        '''
        return self._table.c

    @property
    def c(self) -> sqlalchemy.sql.base.ImmutableColumnCollection:
        '''Alias for self.columns.
        '''
        return self._table.c
    
    @property
    def engine(self) -> ConnectEngine:
        return self._engine
    
    @property
    def schema(self) -> DataclassSchema:
        return self._schema
    
    def list_tables(self) -> typing.List[str]:
        return self._engine.list_tables()
    
    def colnames(self) -> typing.List[str]:
        return [c.name for c in self.columns]

    def primary_keys(self) -> typing.List[str]:
        return [c['name'] for c in self.schema_info() if c['primary_key']]
    
    def schema_info(self):
        '''Get info about each column as a dictionary.
        Returns:
            dict<dict>: info about each column.
        '''
        return self._engine.schema(self._tabname)
    
    def schema_table(self) -> pd.DataFrame:
        '''Get info about each column as a dictionary.
        Returns:
            DataFrame: info about each column.
        '''
        return self._engine.schema_df(self._tabname)
    
    def indices(self) -> typing.List[typing.Dict[str, typing.Any]]:
        return self._engine.inspector.get_indexes(self._tabname)
    
    #################### Expose Query Functionality ###################
    
    @property
    def q(self) -> Query:
        '''Gets a query object for this doctable.'''
        return Query(self)
    


    ################# CRITICAL SQL METHODS ##################
    
    def execute(self, query, *params, verbose=None, **kwargs) -> sqlalchemy.engine.ResultProxy:
        '''Execute an sql command. Called by most higher-level functions.
        Args:
            query (sqlalchemy condition or str): query to execute;
                can be provided as sqlalchemy condition object or
                plain sql text.
            verbose (bool or None): Print SQL command issued before
                execution.
        '''
        prstr = 'DocTable: {}'
        if verbose is not None:
            if verbose: print(prstr.format(query))
        elif self.verbose: print(prstr.format(query))
        
        return self._execute(query, *params, **kwargs)
    
    def _execute(self, query, *params, conn: sqlalchemy.engine.Connection = None) -> sqlalchemy.engine.ResultProxy:
        '''Execute sql query using either existing connection, provided connection, or without a connection.
        '''
        # takes raw query object
        if conn is not None:
            r = conn.execute(query, *params)
        elif self._conn is not None:
            r = self._conn.execute(query, *params)
        else:
            # execute query using connectengine directly
            r = self._engine.execute(query, *params)
        return r









    

    ################# DEPRICATED: ALL BELOW THIS HAS BEEN DEPRICATED ##################




    ################# INSERT METHODS ##################
            
    def insert(self, 
            rowdata: typing.Union[DocTableSchema, typing.Dict[str, typing.Any], typing.List[DocTableSchema], typing.List[typing.Dict[str, typing.Any]]],
            *args, 
            **kwargs,
        ):
        '''Depricated. See docs for .q.insert_single() or .q.insert_multi().'''
        warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
            '.q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.')
        
        if is_sequence(rowdata):
            return self.insert_many(rowdata, *args, **kwargs)
        else:
            return self.insert_single(rowdata, *args, **kwargs)
    
    def insert_many(self, 
            rowdata: typing.Union[typing.List[DocTableSchema], typing.List[typing.Dict[str, typing.Any]]],
            *args, 
            **kwargs
        ):
        '''Depricated. See docs for .q.insert_multi(), .q.insert_multi_raw()'''
        warnings.warn(f'.insert_many() is depricated: please use .q.insert_multi() or '
            '.q.insert_multi_raw()')
        if not is_sequence(rowdata):
            raise TypeError('insert_many needs a list or tuple of schema objects.')
        
        if len(rowdata) > 0 and isinstance(rowdata[0], dict):
            return self.q.insert_multi_raw(rowdata, *args, **kwargs)
        else:
            return self.q.insert_multi(rowdata, *args, **kwargs)
    
    def insert_single(self, rowdata: typing.Union[DocTableSchema, typing.Dict[str, typing.Any]], *args, **kwargs):
        '''Depricated. See docs for .q.insert_single(), .q.insert_single_raw().'''
        warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
            '.q.insert_single_raw()')
        
        if isinstance(rowdata, dict):
            return self.q.insert_single_raw(rowdata, *args, **kwargs)
        else:
            return self.q.insert_single(rowdata, *args, **kwargs)
    
    ################# SELECT METHODS ##################
    
    def count(self, *args, **kwargs):
        '''Depricated. See docs for .q.count(), Query.count().'''
        warnings.warn('Method .count() is depricated. Please use .q.count() instead.')
        return self.q.count(*args, **kwargs)
        
    def head(self, cols: typing.List[sqlalchemy.Column] = None, **kwargs):
        '''Depricated. See docs for .q.select_head(), Query.select_head().'''
        warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')
        if not is_sequence(cols) and cols is not None:
            cols = [cols]
        return self.q.select_head(cols=cols, **kwargs)

    def select_series(self, col: sqlalchemy.Column = None, **kwargs):
        '''Depricated. See docs for .q.select_series(), Query.select_series().'''
        warnings.warn('Method .select_series() is depricated. Please use .q.select_series() instead.')
        return self.q.select_series(col=col, **kwargs)

    def select_df(self, cols: typing.List[sqlalchemy.Column] = None, **kwargs):
        '''Depricated. See docs for .q.select_df(), Query.select_df().'''
        warnings.warn('Method .select_df() is depricated. Please use .q.select_df() instead.')
        if not is_sequence(cols) and cols is not None:
            cols = [cols]
        return self.q.select_df(cols=cols, **kwargs)
    
    def select_first(self, cols: typing.List[sqlalchemy.Column] = None, as_dataclass: bool = None, **kwargs):
        '''Depricated. See docs for .q.select_first(), Query.select_first().'''
        warnings.warn('Method .select_first() is depricated. Please use .q.select_first() instead.')
        if as_dataclass is not None:
            warnings.warn(f'The "as_dataclass" parameter has been depricated: please set get_raw=True or '
                'select_raw to specify that you would like to retrieve a raw RowProxy pobject.')
        
        if not is_sequence(cols) and cols is not None:
            return self.q.select_scalar(col=cols, **kwargs)
            
        else:

            # determine to get result as a dataclass or not
            raw_result = as_dataclass is not None and not as_dataclass
            
            try:
                return self.q.select_first(cols=cols, raw_result=raw_result, **kwargs)
            except RowToObjectConversionFailedError as e:
                warnings.warn(f'Conversion from row to object failed according to the following '
                    f'error. Please use .q.select_first(..,raw_result=True) next time '
                    f'in the future to avoid this issue. {e=}')
                return self.q.select_first(cols=cols, raw_result=True, **kwargs)
            
            
    
    def select(self, cols: typing.List[sqlalchemy.Column] = None, as_dataclass: bool = None, **kwargs):
        '''Depricated. See docs for .q.select(), Query.select().'''
        warnings.warn('Method .select() is depricated. Please use .q.select() instead.')
        if as_dataclass is not None:
            warnings.warn(f'The "as_dataclass" parameter has been depricated: please set get_raw=True or '
                'select_raw to specify that you would like to retrieve a raw RowProxy pobject.')
        
        raw_result = as_dataclass is not None and not as_dataclass
        if not is_sequence(cols) and cols is not None:
            return self.q.select_col(col=cols, **kwargs)
        else:
            if raw_result:
                return self.q.select_raw(cols=cols, **kwargs)
            else:
                try:
                    return self.q.select(cols=cols, **kwargs)
                except RowToObjectConversionFailedError as e:
                    warnings.warn(f'Conversion from row to object failed according to the following '
                        f'error. Please use .q.select_raw() when requesting non-object formatted '
                        f'data such as counts or sums in the future. For now it is automatically '
                        f'converted. {e=}')
                    return self.q.select_raw(cols=cols, **kwargs)


    def join(self, other: DocTable, *args, **kwargs):
        ''' Wrapper over table.join(), can pass to from_obj parameter for .select()
        Args:
            other (DocTable): other doctable to join
            *args, **kwargs: passed to table.join() method
        '''
        return self.table.join(other._table, *args, **kwargs)
    
    
    #################### Select/Insert in Chunk Methods ###################
    
    def select_chunks(self, *args, **kwargs):
        '''Depricated: see docs for .q.select_chunks()'''
        return self.q.select_chunks(*args, **kwargs)
                
    def select_iter(self, *args, **kwargs):
        '''Depricated. See docs for .q.select_iter.'''
        warnings.warn(f'.select_iter() is depricated. Please use .q.select_iter()')
        return self.q.select_iter(*args, **kwargs)
                
    def get_queueinserter(self, **kwargs):
        ''' Get an object that will queue rows for insertion.
        '''
        warnings.warn(f'.get_queueinserter() has been depricated entirely. please'
            'avoid using it.')
        return QueueInserter(self, **kwargs)

    #################### Update and Delete Methods ###################
    def update(self, *args, **kwargs):
        '''Depricated. See docs for .q.update(), Query.update().'''
        warnings.warn('Method .update() is depricated. Please use .q.update() instead.')
        return self.q.update(*args, **kwargs)

    def delete(self, *args, delete_all: bool = True, **kwargs):
        '''Depricated. See docs for .q.delete(), Query.delete().'''
        warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')
        return self.q.delete(*args, delete_all=delete_all, **kwargs)
    
    
    #################### Bootstrapping Methods ###################
    
    def bootstrap(self, *args, n=None, **kwargs):
        '''Generates a DocBootstrapper object to sample from.
        Notes:
            The DocBootstrap object keeps all selected docs in
                memory, and yields samples with .sample().
        Args:
            *args: passed to .select()
            n (int): number of samples to bs. If left unset, can
                specify when drawing sample from DocBootstrap obj.
            **kwargs: passed to .select()
        Returns:
            DocBootstrap object for bootstrapping.
        '''
        docs = self.select(*args, **kwargs)
        return DocBootstrap(docs, n=n)
    
    
    
    
    ################# FILE COLUMN METHODS ##################

    def clean_col_files(self, col, check_missing=True, delete_extraneous=True):
        '''Make sure there is a 1-1 mapping between files listed in db and files in folder.
        Args:
            col (str or Column object): column to clean picklefiles for.
            ignore_missing (bool): if False, throw an error when a db file doesn't exist.
        '''
        col = self.col(col)
        if not isinstance(col.type, FileTypeBase):
            raise ValueError(f'{col} is not a file type; only call clean_col_files for a file column types.')
        if not (check_missing or delete_extraneous):
            raise ValueError('Either check_missing or delete_extraneous should be set to true, '
                             'or else this method does nothing.')
        
        # get column filenames
        with col.type.control:
            db_fnames = set(self.select(col, where=col != None))
        
        # get existing files from filesystem
        fpath = f'{col.type.path}/*{col.type.file_ext}'
        exist_fnames = set(glob(fpath))
        intersect = db_fnames & exist_fnames
        #print(db_fnames, exist_fnames)
        
        # remove files not listed in db
        extraneous_fnames = exist_fnames - intersect
        if delete_extraneous and len(extraneous_fnames) > 0:
            for rm_fname in extraneous_fnames:
                os.remove(rm_fname)
        
        # throw error if filesystem is missing some files
        miss_fnames = db_fnames-intersect
        if check_missing and len(miss_fnames) > 0:
            raise FileNotFoundError('These files were not found while cleaning: {}'
                ''.format(miss_fnames))
        