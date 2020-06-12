import collections
from time import time
import pprint
import random
import pandas as pd
import os
from glob import glob
from datetime import datetime

# operators like and_, or_, and not_, functions like sum, min, max, etc
import sqlalchemy as sa

#from .coltypes import CpickleType, ParseTreeType, PickleFileType, TextFileType, FileTypeBase, JSONType
from .bootstrap import DocBootstrap
#from .util import list_tables
from .connectengine import ConnectEngine
from .schemas import parse_schema

def is_ord_sequence(obj):
    return isinstance(obj, list) or isinstance(obj,tuple)

class DocTable:
    def __init__(self, target=':memory:', tabname='_documents_', schema=None, 
                 persistent_conn=True, verbose=False, new_db=False, engine=None, 
                 dialect='sqlite', **engine_kwargs):
        '''Create new database.
        Args:
            schema (list<list>): schema from which to create db. Includes a
                list of columns (including contraints and indexes) as tuples
                defined according to information needed to execute the sqlalchemy
                commands.
            tabname (str): table name for this specific doctable.
            target (str): filename for database to connect to. ":memory:" is a 
                special value indicating to the python db engine that the db
                should be created in memory. Will create new empty database file
                if it does not exist and new_db is True.
            dialect (str): database engine through which to construct db.
                For more info, see sqlalchemy dialect info:
                https://docs.sqlalchemy.org/en/13/dialects/
            persistent_conn (bool): whether or not to create a persistent conn 
                to database. Set to True to lock db from other process access 
                while instance exists, esp if calling .update() in a .select()
                loop. Set to False to access from separate processes.
            verbose (bool): Print every sql command before executing.
            new_db (bool): Indicate if new db file should be created given 
                that a schema is provided and the db file doesn't exist.
            engine_args (**kwargs): Pass directly to the sqlalchemy
                .create_engine(). Args typically vary by dialect.
                Example: connect_args={'timeout': 15} for sqlite
                or connect_args={'connect_timeout': 15} for PostgreSQL.
        '''
        # static definition variable assignments
        try:
            kwargs = self.args # user can provide their own data
            if 'tabname' in kwargs:
                tabname = kwargs['tabname']
            if 'schema' in kwargs:
                schema = kwargs['schema']
            if 'target' in kwargs:
                target = kwargs['target']
            if 'verbose' in kwargs:
                verbose = kwargs['verbose']
            if 'new_db' in kwargs:
                new_db = kwargs['new_db']
            if 'dialect' in kwargs:
                dialect = kwargs['dialect']
            if 'engine_kwargs' in kwargs:
                engine_kwargs = kwargs['engine_kwargs']
        except AttributeError:
            pass
        try:
            tabname = self.tabname
        except AttributeError:
            pass
        try:
            schema = self.schema
        except AttributeError:
            pass
        try:
            target = self.target
        except AttributeError:
            pass
        
        if dialect.startswith('sqlite'):
            if schema is None and (target == ':memory:' or not os.path.exists(target)):
                raise ValueError('Schema must be provided if using memory database or '
                             'database file does not exist yet. Need to provide schema '
                             'when creating a new table.')
        
        # store arguments as-is
        self._tabname = tabname
        self._target = target
        self.verbose = verbose
        self.user_schema = schema
        self.persistent_conn = persistent_conn
        
        # establish an engine connection
        if engine is None:
            self._engine = ConnectEngine(dialect=dialect, target=target, new_db=new_db, 
                                     **engine_kwargs)
        else:
            self._engine = engine
        
        # connect to existing table or create new one
        self._columns = None
        if schema is not None:
            self._columns = parse_schema(schema, target+'_'+tabname)
        
        self._table = self._engine.add_table(self._tabname, columns=self._columns)
        
        # connect to database
        self._conn = self._engine.get_connection()
        
    def __delete__(self):
        ''' Closes database connection to prevent locking db.
        '''
        self.close_conn()
    
    #################### Convenience Methods ###################
    
    def __str__(self):
        return '<DocTable::{} ct: {}>'.format(self._tabname, self.count())
    
    def __repr__(self):
        return str(self)
    
    def __getitem__(self, colname):
        '''Accesses a column object by calling .col().'''
        return self.col(colname)
    
    def col(self,name):
        '''Accesses a column object.
        Args:
            Name of column to access. Applied as subscript to 
                sqlalchemy columns object.
        '''
        if isinstance(name, sa.Column):
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
    
    def schema_info(self):
        '''Get info about each column as a dictionary.
        Returns:
            dict<dict>: info about each column.
        '''
        return self._engine.schema()
    
    def schema_table(self):
        '''Get info about each column as a dictionary.
        Returns:
            DataFrame: info about each column.
        '''
        return self._engine.schema_table(self._tabname)
    
            
    #################### Connection Methods ###################
    
    def close_conn(self):
        ''' Closes connection to db (if one exists). '''
        if self._conn is not None:
            self._conn.close()
            self._conn = None
        
    def open_conn(self):
        ''' Opens connection to db (if one does not exist). '''
        if not self._engine.is_open():
            raise ValueError('Need to create engine using .open_engine() '
                             'before trying to open connection.')
        
        if self._conn is None:
            self._conn = self._engine.get_connection()
    
    def open_engine(self, open_conn=None):
        ''' Opens connection engine. 
            open_conn overrides persistent_conn if defined
            default is True
        '''
        self._engine.open()
        #self._table = self._engine.add_table(self._tabname, columns=self._columns)
        
        if open_conn or (open_conn is None and self.persistent_conn):
            self.open_conn()
    
    def close_engine(self):
        ''' Closes connection engine. '''
        self.close_conn()
        self._engine.close()
        
    
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
        q = sa.sql.insert(self._table, rowdat)
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
    
    
    def count(self, where=None, whrstr=None, **kwargs):
        '''Count number of rows which match where condition.
        Notes:
            Calls select_first under the hood.
        Args:
            where (sqlalchemy condition): filter rows before counting.
            whrstr (str): filter rows before counting.
        Returns:
            int: number of rows that match "where" and "whrstr" criteria.
        '''
        cter = sa.sql.func.count(self._table)
        ct = self.select_first(cter, where=where, whrstr=whrstr, **kwargs)
        return ct
    
    def head(self, n=5):
        ''' Return first n rows as dataframe for quick viewing.
        Args:
            n (int): number of rows to return in dataframe.
        Returns:
            Dataframe of the first n rows of the table.
        '''
        return self.select_df(limit=n)
    
    def select(self, cols=None, where=None, orderby=None, groupby=None, limit=None, whrstr=None, offset=None, **kwargs):
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
            whrstr (str): raw sql "where" conditionals to add to where input
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
        result = self._exec_select_query(cols,where,orderby,groupby,limit,whrstr,offset,**kwargs)
        # this is the result object:
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        
        # NOTE: I USE LIST RETURN BECAUSE UNDERLYING SQL ENGINE
        # WILL LOAD THE DATA INTO MEMORY ANYWAYS. THIS JUST PRESENTS
        # A MORE FLEXIBLE INTERFACE TO THE USER.
        # row is an object that can be accessed by col keyword
        # i.e. row['id'] or num index, i.e. row[0].
        if return_single:
            return [row[0] for row in result]
        else:
            return [row for row in result]
    
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
        
        sel = self.select(cols, *args, **kwargs)
        rows = [dict(r) for r in sel]
        return pd.DataFrame(rows)
    
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
    
    def _exec_select_query(self, cols, where, orderby, groupby, limit, whrstr, offset,**kwargs):
        
        q = sa.sql.select(cols)
        
        if where is not None:
            q = q.where(where)
        if whrstr is not None:
            q = q.where(sa.text(whrstr))
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
    
    def update(self, values, where=None, whrstr=None, **kwargs):
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
            whrstr (sql string condition): matches same as where arg.
        Returns:
            SQLAlchemy result proxy object
        '''
            
        # update the main column values
        if isinstance(values,list) or isinstance(values,tuple):
            q = sa.sql.update(self._table, preserve_parameter_order=True)
            q = q.values(values)
        else:
            q = sa.sql.update(self._table)
            q = q.values(values)
        
        if where is not None:
            q = q.where(where)
        if whrstr is not None:
            q = q.where(sa.text(whrstr))
        
        r = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    
    #################### Delete Methods ###################
    
    def delete(self, where=None, whrstr=None, vacuum=False, **kwargs):
        '''Delete rows from the table that meet the where criteria.
        Args:
            where (sqlalchemy condition): criteria for deletion.
            whrstr (sql string): addtnl criteria for deletion.
            vacuum (bool): will execute vacuum sql command to reduce
                storage space needed by SQL table. Use when deleting
                significant ammounts of data.
        Returns:
            SQLAlchemy result proxy object.
        '''
        q = sa.sql.delete(self._table)

        if where is not None:
            q = q.where(where)
        if whrstr is not None:
            q = q.where(sa.text(whrstr))
        
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
        prstr = 'DocTable2 Query: {}'
        if verbose is not None:
            if verbose: print(prstr.format(query))
        elif self.verbose: print(prstr.format(query))
        
        # try to parse
        result = self._execute(query, **kwargs)
        return result
    
    def _execute(self, query, conn=None):
        if not self._engine.is_open():
            raise AttributeError('DocTable does not have an engine '
                'connection. Use .open_engine() to make new engine '
                'connection.')
        
        # takes raw query object
        if conn is not None:
            r = conn.execute(query)
        elif self._conn is not None:
            r = self._conn.execute(query)
        else:
            with self._engine.get_connection() as conn:
                r = conn.execute(query)
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
        if not isinstance(self.col(col).type, FileTypeBase):
            raise ValueError('Only call clean_col_files for a file column types.')
        if not (check_missing or delete_extraneous):
            raise ValueError('Either check_missing or delete_extraneous should be set to true, '
                             'or else this method does nothing.')
        
        # get column filenames
        db = DocTable(tabname=self._tabname, engine=self._engine)
        dbcol = db[col.name]
        db_fnames = {col.type.fpath+fn for fn in db.select(dbcol, where=dbcol != None)}
        
        # get existing files from filesystem
        exist_fnames = set(glob(col.type.fpath+'*'+col.type.file_ext))
        intersect = db_fnames & exist_fnames
        
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
