import collections
from time import time
import pprint
import random
import pandas as pd
import os
from glob import glob
from datetime import datetime
import typing
from typing import Union, Mapping, Sequence, Tuple, Set, List
import dataclasses

# operators like and_, or_, and not_, functions like sum, min, max, etc
#import sqlalchemy as sa
import sqlalchemy

from .schemas import FileTypeBase
from .model import DocBootstrap
#from .util import list_tables
from .connectengine import ConnectEngine
from .schemas import parse_schema_strings, parse_schema_dataclass, DocTableRow

class DocTable:
    ''' Class for managing a single database table.
    Description: This class manages schema and connection information to provide
        an object-based interface to perform queries on a single table 
        in a database (although multi-table designs are possible with 
        multiple DocTables). It is designed to maintain informabout about the 
        underlying database structure of the table, making it possible to 
        execute queries without using the SQL language.

    Settable static attributes (overridden if related constructor argument passed):
        _tabname_ (str): name of table to connect to (and create).
        _schema_ (str): schema definition for this doctable, to be used
            when creating a new table and to manage table information.
        _target_ (str): target database to connect to - used when a doctable
            will always connect to the same target (i.e., a server etc).
        _doctable_args_ (dict): any other constructor arguments that should always
            be used when instantiating. Overridden by providing arguments
            to the constructor.
    '''
    __default_tabname__ = '_documents_'
    def __init__(self, target: str = None, tabname: str = None, schema: Sequence[Sequence] = None,
                dialect='sqlite', engine=None, readonly=False, new_db=False, new_table=True, 
                persistent_conn=True, verbose=False, **engine_kwargs):
        '''Create new database.
        Args:
            target (str): filename for database to connect to. ":memory:" is a 
                special value indicating to the python sqlite engine that the db
                should be created in memory. Will create new empty database file
                if it does not exist and new_db==True, and add a new table using
                specified schema if new_table==True.
            schema (list<list>): schema from which to create db. Includes a
                list of column names and types (including contraints and indexes) as tuples
                defined according to information needed to construct the sqlalchemy
                objects.
            tabname (str): table name for this specific doctable.
            dialect (str): database engine through which to construct db.
                For more info, see sqlalchemy dialect info:
                https://docs.sqlalchemy.org/en/13/dialects/
            persistent_conn (bool): whether or not to create a persistent conn 
                to database. Otherwise will create temporary connection for each
                query.
            readonly (bool): Prevents user from calling insert(), delete(), or 
                update(). Will not block other sql possible commands.
            new_db (bool): Indicate if new db file should be created given 
                that a schema is provided and the db file doesn't exist.
            new_table (bool): Allow doctable to create a new table if one 
                doesn't exist already.
            engine_kwargs (**kwargs): Pass directly to the sqlalchemy
                .create_engine(). Args typically vary by dialect.
                Example: connect_args={'timeout': 15} for sqlite
                or connect_args={'connect_timeout': 15} for PostgreSQL.
            verbose (bool): Print every sql command before executing.
            echo (bool): Print sqlalchemy engine log for each query.
        '''
        
        # target argument
        if engine is not None:
            target = engine.target
        elif target is not None:
            pass # use constructor-provided target
        elif hasattr(self, '_target_'):
            target = self._target_
        elif hasattr(self, '_doctable_args_') and 'target' in self._doctable_args_:
            target = self._doctable_args_.target
        else:
            raise ValueError('target has not been provided.')

        if hasattr(self, '__args__'):
            raise NameError('The __args__ definition has changed to _doctable_args_.')

        # tabname arguments
        if tabname is not None:
            pass # use constructor-provided tabname
        elif hasattr(self, '__tabname__'):
            raise NameError('The __tabname__ definition has changed to _tabname_.')
        elif hasattr(self, '_tabname_'):
            tabname = self._tabname_
        elif hasattr(self, '_doctable_args_') and 'tabname' in self._doctable_args_:
            tabname = self._doctable_args_.tabname
        else:
            tabname = self.__default_tabname__

        # schema arguments
        if schema is not None:
            pass # use constructor-provided schema
        elif hasattr(self, '__schema__'):
            raise NameError('The __schema__ definition has changed to _schema_.')
        elif hasattr(self, '_schema_'):
            schema = self._schema_
        elif hasattr(self, '_doctable_args_') and 'schema' in self._doctable_args_:
            schema = self._doctable_args_.schema
        else:
            schema = None
        
        # overwrite arg defaults if provided in _doctable_args_
        if hasattr(self, '_doctable_args_'):
            if dialect is None and 'dialect' in self._doctable_args_:
                dialect = self._doctable_args_['dialect']
            if verbose is None and 'verbose' in self._doctable_args_:
                verbose = self._doctable_args_['verbose']
            if new_db is None and 'new_db' in self._doctable_args_:
                new_db = self._doctable_args_['new_db']
            if engine_kwargs is None and 'engine_kwargs' in self._doctable_args_:
                engine_kwargs = self._doctable_args_['engine_kwargs']
        
        # dependent args
        if readonly:
            new_db = False
            new_table = False
        
        # some error checking
        if dialect.startswith('sqlite'):
            if schema is None and engine is None and (target == ':memory:' or not os.path.exists(target)):
                raise ValueError('Schema must be provided if using memory database or '
                             'database file does not exist yet. Need to provide schema '
                             'when creating a new table.')
        
        # store arguments as-is
        self._tabname = tabname
        self._target = target
        self.verbose = verbose
        self._schema = schema
        self.persistent_conn = persistent_conn
        self._readonly = readonly
        self._new_db = new_db
        self._new_table = new_table
        
        # establish an engine connection
        if engine is None:
            self._engine = ConnectEngine(target=target, dialect=dialect, new_db=new_db, 
                                     **engine_kwargs)
        else:
            self._engine = engine
        
        # connect to existing table or create new one
        if dataclasses.is_dataclass(schema):
            if not issubclass(schema, DocTableRow):
                raise TypeError('A dataclass schema must inherit from doctable.DocTableRow.')
            self._columns = parse_schema_dataclass(schema)
        elif isinstance(schema, list) or isinstance(schema, tuple):
            self._columns = parse_schema_strings(schema, target+'_'+tabname)
        else:
            self._columns = None # inferred from existing table
        
        self._table = self._engine.add_table(self._tabname, columns=self._columns, 
                                             new_table=self._new_table)
        
        # connect to database
        self._conn = self._engine.connect()
        
    def __del__(self):
        ''' Closes database connection to prevent locking db.
        '''
        # apparently engines and connections are garbage collected using event handlers?
        # I don't understand this, but solved some big issues by just doing nothing.
        
        #self._engine.remove_table(self._table) # remove from engine metadata
        #self.close_conn()
        pass

        
    
    #################### Connection Methods ###################
    
    def close_conn(self):
        ''' Closes connection to db (if one exists). '''
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            
        
    def open_conn(self):
        ''' Opens connection to db (if one does not exist). '''
        
        if self._conn is None:
            self._conn = self._engine.connect()
    
    def reopen_engine(self, open_conn=None):
        ''' Opens connection engine. 
        Args:
            open_conn (bool): create a new db connection.
        '''
        self.close_conn()
        self._engine.reopen()
        if open_conn or (open_conn is None and self.persistent_conn):
            self.open_conn()


    #################### Convenience Methods ###################
    
    def __str__(self) -> str:
        return f'<DocTable ({len(self.columns)} cols)::{repr(self._engine)}:{self._tabname}>'
    
    def __getitem__(self, colname):
        '''Accesses a column object by calling .col().'''
        return self.col(colname)
    
    def col(self,name):
        '''Accesses a column object.
        Args:
            Name of column to access. Applied as subscript to 
                sqlalchemy columns object.
        '''
        if isinstance(name, sqlalchemy.Column):
            return name
        return self._table.c[name]
        
    @property
    def table(self):
        '''Returns underlying sqlalchemy table object for manual manipulation.
        '''
        return self._table
    
    @property
    def tabname(self):
        '''Gets name of table for this connection.'''
        return self._tabname
    
    @property
    def columns(self):
        '''Exposes SQLAlchemy core table columns object.
        Notes:
            some info here: 
            https://docs.sqlalchemy.org/en/13/core/metadata.html
            
            c = db.columns['id']
            c.type, c.name, c.
        Returns:
            sqlalchemy columns: access to underlying columns
                object.
        '''
        return self._table.c
    
    @property
    def engine(self):
        return self._engine
    
    def list_tables(self):
        return self._engine.list_tables()
    
    def colnames(self):
        return [c.name for c in self.columns]

    def primary_keys(self):
        return [c['name'] for c in self.schema_info() if c['primary_key']]
    
    def schema_info(self):
        '''Get info about each column as a dictionary.
        Returns:
            dict<dict>: info about each column.
        '''
        return self._engine.schema(self._tabname)
    
    def schema_table(self):
        '''Get info about each column as a dictionary.
        Returns:
            DataFrame: info about each column.
        '''
        return self._engine.schema_df(self._tabname)
    
    ################# INSERT METHODS ##################
    
    def insert(self, rowdat, ifnotunique='fail', **kwargs):
        '''Insert a row or rows into the database.
        Args:
            rowdat (list<dict> or dict): row data to insert.
            ifnotunique (str): way to handle inserted data if it breaks
                a table constraint. Choose from FAIL, IGNORE, REPLACE.
        Returns:
            sqlalchemy query result object.
        '''
        if self._readonly:
            raise ValueError('Cannot call .insert() when doctable set to readonly.')

        if dataclasses.is_dataclass(self._schema):
            if isinstance(rowdat, DocTableRow):
                rowdat = rowdat._doctable_as_dict()
            
            elif is_sequence(rowdat) and len(rowdat) > 0 and isinstance(rowdat[0], DocTableRow):
                rowdat = [r._doctable_as_dict() for r in rowdat]
        
        q = sqlalchemy.sql.insert(self._table, rowdat)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        
        #NOTE: there is a weird issue with using verbose mode with a 
        #  multiple insert. The printing interface is not aware of 
        #  the SQL dialect and therefore throws an error.
        
        # To print correctly, would need something like this:
        #from sqlalchemy.dialects import mysql
        #print str(q.statement.compile(dialect=mysql.dialect()))
        
        if is_sequence(rowdat):
            if 'verbose' in kwargs:
                del kwargs['verbose']
            r = self.execute(q, verbose=False, **kwargs)
        else:
            r = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    ################# SELECT METHODS ##################
    
    
    def count(self, where=None, wherestr=None, **kwargs):
        '''Count number of rows which match where condition.
        Notes:
            Calls select_first under the hood.
        Args:
            where (sqlalchemy condition): filter rows before counting.
            wherestr (str): filter rows before counting.
        Returns:
            int: number of rows that match "where" and "wherestr" criteria.
        '''
        cter = sqlalchemy.sql.func.count(self._table)
        ct = self.select_first(cter, where=where, wherestr=wherestr, **kwargs)
        return ct
    
    def head(self, n=5):
        ''' Return first n rows as dataframe for quick viewing.
        Args:
            n (int): number of rows to return in dataframe.
        Returns:
            Dataframe of the first n rows of the table.
        '''
        return self.select_df(limit=n)
    
    def select(self, cols=None, where=None, orderby=None, groupby=None, limit=None, wherestr=None, offset=None, from_obj=None, as_dataclass=True, result_container=list, **kwargs):
        '''Perform select query, yield result for each row.
        
        Description: Because output must be iterable, returns special column results 
            by performing one query per row. Can be inefficient for many smaller 
            special data information.
        
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
            wherestr (str): raw sql "where" conditionals to add to where input
            from_obj (sqlalchemy join): table from which to perform query (for joined tables)
            as_dataclass (bool): if schema was provided in dataclass format, should return as 
                dataclass object?
            result_container (class): container for result rows. constructor takes single arg
                may be useful to provide a class that extends list
            **kwargs: passed to self.execute()
        Yields:
            sqlalchemy result object: row data
        '''
        return_single = False
        if cols is None:
            cols = list(self._table.columns)
        else:
            if not is_sequence(cols):
                return_single = True
                cols = [cols]
        cols = [c if not isinstance(c,str) else self[c] for c in cols]
                
        # query colunmns in main table
        result = self._exec_select_query(cols,where,orderby,groupby,limit,wherestr,offset,from_obj,**kwargs)
        # this is the result object:
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        
        # NOTE: I USE LIST RETURN BECAUSE UNDERLYING SQL ENGINE
        # WILL LOAD THE DATA INTO MEMORY ANYWAYS. THIS JUST PRESENTS
        # A MORE FLEXIBLE INTERFACE TO THE USER.
        # row is an object that can be accessed by col keyword
        # i.e. row['id'] or num index, i.e. row[0].
        if return_single:
            return result_container(row[0] for row in result.fetchall())
        else:
            if dataclasses.is_dataclass(self._schema) and as_dataclass:
                return result_container(self._schema(**row) for row in result.fetchall())
            else:
                if result_container is list:
                    return result.fetchall()
                else:
                    return result_container(result.fetchall())
    
    def select_first(self, *args, **kwargs):
        '''Perform regular select query returning only the first result.
        Args:
            *args: args to regular .select() method.
            **kwargs: args to regular .select() method.
        Returns:
            sqlalchemy results obect: First result from select query.
        Raises:
            LookupError: where no items are returned with the select 
                statement. Couldn't return None or other object because
                those could be valid objects in a single-row select query.
                In cases where uncertain if row match exists, use regular 
                .select() and count num results, or use try/catch.
        '''
        result = self.select(*args, limit=1, **kwargs)
        if len(result) == 0:
            raise LookupError('No results were returned. Needed to error '
                'so this result wasn not confused with case where actual '
                'result is None. If not sure about result, use regular '
                '.select() method with limit=1.')
        return result[0]
    
    def select_df(self, cols=None, *args, **kwargs):
        '''Select returning dataframe.
        Args:
            cols: sequence of columns to query. Must be sequence,
                passed directly to .select() method.
            *args: args to regular .select() method.
            **kwargs: args to regular .select() method.
        Returns:
            pandas dataframe: Each row is a database row,
                and output is not indexed according to primary 
                key or otherwise. Call .set_index('id') on the
                dataframe to envoke this behavior.
        '''
        if cols is None:
            cols = list(self._table.columns)
        elif not is_sequence(cols):
            cols = [cols]
        
        sel = self.select(cols, *args, as_dataclass=False, **kwargs)
        return pd.DataFrame([dict(r) for r in sel])
    
    def select_series(self, col, *args, **kwargs):
        '''Select returning pandas Series.
        Args:
            col: column to query. Passed directly to .select() 
                method.
            *args: args to regular .select() method.
            **kwargs: args to regular .select() method.
        Returns:
            pandas series: enters rows as values.
        '''
        if is_sequence(col):
            raise TypeError('col argument should be single column.')
        
        sel = self.select(col, *args, **kwargs)
        return pd.Series(sel)
    
    def _exec_select_query(self, cols, where, orderby, groupby, limit, wherestr, offset, from_obj, **kwargs):
        
        if from_obj is None:
            q = sqlalchemy.sql.select(cols)
        else:
            q = sqlalchemy.sql.select(cols, from_obj=from_obj)
        
        if where is not None:
            q = q.where(where)
        if wherestr is not None:
            q = q.where(sqlalchemy.text(f'({wherestr})'))
        if orderby is not None:
            if is_sequence(orderby):
                q = q.order_by(*orderby)
            else:
                q = q.order_by(orderby)
        if groupby is not None:
            if is_sequence(groupby):
                q = q.group_by(*groupby)
            else:
                q = q.group_by(groupby)
            
        if limit is not None:
            q = q.limit(limit)
        if offset is not None:
            q = q.offset(offset)
        
        result = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return result

    def join(self, other, *args, **kwargs):
        ''' Wrapper over table.join(), can pass to from_obj parameter for .select()
        Args:
            other (DocTable): other doctable to join
            *args, **kwargs: passed to table.join() method
        '''
        return self._table.join(other._table, *args, **kwargs)
    
    
    #################### Select in Chunk Methods ###################
    
    def select_chunks(self, cols=None, chunksize=100, limit=None, **kwargs):
        ''' Performs select while querying only a subset of the results at a time.
        Args:
            cols (col name(s) or sqlalchemy object(s)): columns to query
            chunksize (int): size of individual queries to be made. Will
                load this number of rows into memory before yielding.
            limit (int): maximum number of rows to retrieve. Because 
                the limit argument is being used internally to limit data
                to smaller chunks, use this argument instead. Internally,
                this function will load a maximum of limit + chunksize 
                - 1 rows into memory, but yields only limit.
        Yields:
            sqlalchemy result: row data - same as .select() method.
        '''
        offset = 0
        while True:
            rows = self.select(cols, offset=offset, limit=chunksize, **kwargs)
            chunk = rows[:limit-offset] if limit is not None else rows
            
            yield chunk
            
            offset += len(rows)
            
            if (limit is not None and offset >= limit) or len(rows) == 0:
                break
                
    def select_iter(self, cols=None, chunksize=1, limit=None, **kwargs):
        ''' Same as .select except results retrieved from db in chunks.
        Args:
            cols (col name(s) or sqlalchemy object(s)): columns to query
            chunksize (int): size of individual queries to be made. Will
                load this number of rows into memory before yielding.
            limit (int): maximum number of rows to retrieve. Because 
                the limit argument is being used internally to limit data
                to smaller chunks, use this argument instead. Internally,
                this function will load a maximum of limit + chunksize 
                - 1 rows into memory, but yields only limit.
        Yields:
            sqlalchemy result: row data - same as .select() method.
        '''
        for chunk in self.select_chunks(cols=cols, chunksize=chunksize, 
                                                    limit=limit, **kwargs):
            for row in chunk:
                yield row
                
    
    #################### Update Methods ###################
    
    def update(self, values, where=None, wherestr=None, **kwargs):
        '''Update row(s) assigning the provided values.
        Args:
            values (dict<colname->value> or list<dict> or list<(col,value)>)): 
                values to populate rows with. If dict, will insert those values
                into all rows that match conditions. If list of dicts, assigns
                expression in value (i.e. id['year']+1) to column. If list of 
                (col,value) 2-tuples, will assign value to col in the order 
                provided. For example given row values x=1 and y=2, the input
                [(x,y+10),(y,20)], new values will be x=12, y=20. If opposite
                order [(y,20),(x,y+10)] is provided new values would be y=20,
                x=30. In cases where list<dict> is provided, this behavior is 
                undefined.
            where (sqlalchemy condition): used to match rows where
                update will be applied.
            wherestr (sql string condition): matches same as where arg.
        Returns:
            SQLAlchemy result proxy object
        '''
        if self._readonly:
            raise ValueError('Cannot call .update() when doctable set to readonly.')
            
        # update the main column values
        if isinstance(values,list) or isinstance(values,tuple):
            
            if is_sequence(values) and len(values) > 0 and isinstance(values[0], DocTableRow):
                values = [v._doctable_as_dict() for v in values]
            
            q = sqlalchemy.sql.update(self._table, preserve_parameter_order=True)
            q = q.values(values)
        else:
            if isinstance(values, DocTableRow):
                values = values._doctable_as_dict()

            q = sqlalchemy.sql.update(self._table)
            q = q.values(values)
        
        if where is not None:
            q = q.where(where)
        if wherestr is not None:
            q = q.where(sqlalchemy.text(wherestr))
        
        r = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r

    def update_dataclass(self, obj, key_name=None, **kwargs):
        ''' Updates database with single modified object based on the provided key.
        '''
        if key_name is None:
            keynames = self.primary_keys()
            if not len(keynames):
                raise ValueError('The "primary_key_name" argument should be provided if '
                                    'database has no primary key.')
            key_name = keynames[0]

        return self.update(obj, where=self[key_name]==obj[key_name], **kwargs)
            
        

    
    
    #################### Delete Methods ###################
    
    def delete(self, where=None, wherestr=None, vacuum=False, **kwargs):
        '''Delete rows from the table that meet the where criteria.
        Args:
            where (sqlalchemy condition): criteria for deletion.
            wherestr (sql string): addtnl criteria for deletion.
            vacuum (bool): will execute vacuum sql command to reduce
                storage space needed by SQL table. Use when deleting
                significant ammounts of data.
        Returns:
            SQLAlchemy result proxy object.
        '''
        if self._readonly:
            raise ValueError('Cannot call .delete() when doctable set to readonly.')
        
        q = sqlalchemy.sql.delete(self._table)

        if where is not None:
            q = q.where(where)
        if wherestr is not None:
            q = q.where(sqlalchemy.text(wherestr))
        
        r = self.execute(q, **kwargs)
        
        if vacuum:
            self.execute('VACUUM')
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    ################# CRITICAL SQL METHODS ##################
    
    def execute(self, query, verbose=None, **kwargs):
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
        
        # try to parse
        result = self._execute(query, **kwargs)
        return result
    
    def _execute(self, query, conn=None):
        
        # takes raw query object
        if conn is not None:
            r = conn.execute(query)
        elif self._conn is not None:
            r = self._conn.execute(query)
        else:
            # execute query using connectengine directly
            r = self._engine.execute(query)
        return r
    
    
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
    
    
    
def is_sequence(obj):
    return isinstance(obj, list) or isinstance(obj,set) or isinstance(obj,tuple)

def is_ord_sequence(obj):
    return isinstance(obj, list) or isinstance(obj,tuple)
