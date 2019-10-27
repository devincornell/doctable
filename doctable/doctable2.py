import collections
from time import time
import pprint
import random
import pandas as pd
import os.path

# operators like and_, or_, and not_, functions like sum, min, max, etc
import sqlalchemy.sql as op
from sqlalchemy.sql import func
import sqlalchemy as sa

from .coltypes import CpickleType

class DocTable2:
    _type_map = {
        'biginteger':sa.BigInteger,
        'boolean':sa.Boolean,
        'date':sa.Date,
        'datetime':sa.DateTime,
        'enum':sa.Enum,
        'float':sa.Float,
        'integer':sa.Integer,
        'interval':sa.Interval,
        'largebinary':sa.LargeBinary,
        'numeric':sa.Numeric,
        #'pickle':sa.PickleType,
        'smallinteger':sa.SmallInteger,
        'string':sa.String,
        'text':sa.Text,
        'time':sa.Time,
        'unicode':sa.Unicode,
        'unicodetext':sa.UnicodeText,
        'pickle': CpickleType, # custom datatype
    }
    
    _constraint_map = {
        'unique_constraint': sa.UniqueConstraint,
        'check_constraint': sa.CheckConstraint,
        'primarykey_constraint': sa.PrimaryKeyConstraint,
        'foreignkey_constraint': sa.ForeignKeyConstraint,
        'index': sa.Index,
    }
    _valid_types = list(_constraint_map.keys()) + list(_type_map.keys())
    
    def __init__(self, schema=None, tabname='_documents_', fname=':memory:', engine='sqlite', persistent_conn=True, verbose=False, make_new_db=True, **engine_args):
        '''Create new database.
        Args:
            schema (list<list>): schema from which to create db. Includes a
                list of columns (including contraints and indexes) as tuples
                defined according to information needed to execute the sqlalchemy
                commands.
            tabname (str): table name for this specific doctable.
            fname (str): filename for database to connect to. ":memory:" is a 
                special value indicating to the python db engine that the db
                should be created in memory. Will create new empty database file
                if it does not exist and new_db is True.
            engine (str): database engine through which to construct db.
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
        
        # in cases where user did not want to create new db but a db does not 
        # exist
        if fname != ':memory:' and not os.path.exists(fname) and not make_new_db:
            raise ValueError('new_db is set to true and the database does not '
                             'exist yet.')
        
        # separate tables for custom data types and main table
        self._fname = fname
        self._tabname = tabname
        self.verbose = verbose
        
        connstr = '{}:///{}'.format(engine,fname)
        self._engine = sa.create_engine(connstr, **engine_args)
        self._schema = schema
        
        # make table if needed
        self._metadata = sa.MetaData()
        if self._schema is not None:
            columns = self._parse_column_schema(schema)
            self._table = sa.Table(self._tabname, self._metadata, *columns)
            self._metadata.create_all(self._engine)
        else:
            self._table = sa.Table(self._tabname, self._metadata, 
                                   autoload=True, autoload_with=self._engine)
        
        # bind .min(), .max(), and .count() to col objects themselves.
        self._bind_functions()
            
        # connect with database engine
        self._conn = None
        if persistent_conn:
            self.open_conn()
    
    def __delete__(self):
        '''Closes database connection to prevent locking.'''
        self.close_conn()
            
    def __str__(self):
        return '<DocTable2::{} ct: {}>'.format(self._tabname, self.count())
    
    def close_conn(self):
        '''Closes connection to db (if one exists).
        Notes:
            Primarily to be used if persistent_conn flag was set
                to true in constructor, but user wants to close.
        '''
        if self._conn is not None:
            self._conn.close()
        self._conn = None
		
    def open_conn(self):
        '''Opens connection to db (if one does not exist).
        Notes:
            Primarily to be used if persistent_conn flag was set
                to false in constructor, but user wants to create.
        
        '''
        if self._conn is None:
            self._conn = self._engine.connect()
        
        
    ################# INITIALIZATION METHODS ##################
    
    def _parse_column_schema(self,schema):
        self.colnames = [c[0] for c in schema]
        columns = list()
        for colinfo in schema:
            if len(colinfo) == 2:
                colname, coltype = colinfo
                colargs, coltypeargs = dict(), dict()
            elif len(colinfo) == 3:
                colname, coltype, colargs = colinfo
                coltypeargs = dict()
            elif len(colinfo) == 4:
                colname, coltype, colargs, coltypeargs = colinfo
            else:
                raise ValueError(coltype_error_str)
            
            if coltype not in self._constraint_map: # if coltype is regular column
                typ = self._get_sqlalchemy_type(coltype)
                col = sa.Column(colname, typ(**coltypeargs), **colargs)
                columns.append(col)

            else: # column is actually a constraint (not regular column)
                if coltype  == 'index':
                    const = self._constraint_map[coltype](colname, *colargs, **coltypeargs)
                elif coltype  == 'foreignkey_constraint':
                    # colname is ([col1,col2],[parentcol1,parentcol2])
                    const = self._constraint_map[coltype](*colname, **colargs)
                elif coltype == 'check_constraint':
                    # in this case, colname should be a constraint string (i.e. "age > 0")
                    const = self._constraint_map[coltype](colname, **colargs)
                else:
                    if not is_sequence(colname):
                        raise ValueError('First column argument on {} should '
                            'be a sequence of columns.'.format(coltype))
                    const = self._constraint_map[coltype](*colname, **colargs)
                columns.append(const)
        return columns


                
    def _get_sqlalchemy_type(self,typstr):
        '''Maps typstr to a sqlalchemy data type (or doctable custom type).
        Notes:
            See examples/markdown/dt2_basics.md#type-mappings for more 
                information about type mappings.
        '''
        if typstr not in self._type_map:
            raise ValueError('Provided column type "{}" doesn\'t match '
                'one of {}.'.format(typstr,self._valid_types))
        else:
            return self._type_map[typstr]
    
    def _bind_functions(self):
        '''Binds .max(), .min(), .count() to each column object.
            note: https://docs.sqlalchemy.org/en/13/core/functions.html
        '''
        for col in self._table.c:
            col.max = func.max(col)
            col.min = func.min(col)
            col.count = func.count(col)
            col.sum = func.sum(col)
    
    #################### Convenience Methods ###################
    
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
        cter = func.count(self._table)
        ct = self.select_first(cter, where=where, whrstr=whrstr, **kwargs)
        return ct
    
    def next_id(self, idcol='id', **kwargs):
        '''Returns the highest value in idcol plus one.
        Args:
            idcol (str): column name to look up.
        Returns:
            int: next id to be assigned by autoincrement.
        '''
        # use the results object .inserted_primary_key to get after 
        # inserting. Here is the object returned by insert:
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        
        mx = self.select_first(func.max(self[idcol]), **kwargs)
        if mx is None:
            return 1 # (usually first entry in sql table)
        else:
            return mx + 1
        
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
    def schemainfo(self):
        '''Get info about each column as a dictionary.
        Returns:
            dict<dict>: info about each column.
        '''
        inspector = sa.inspect(self._engine)
        return inspector.get_columns(self._tabname)
    
    def schemainfo_long(self):
        '''Get custom-selected schema information.
        Notes:
            This method is similar to schemainfo, but includes
                more hand-selected information. Likeley to be 
                removed in future versions.
        Returns:
            dict<dict>: info about each column, more info than 
                .schemainfo() provides.
        '''
        info = dict()
        for col in self._table.c:
            ci = dict(
                name=col.name,
                type=col.type,
                comment=col.comment,
                constraints=col.constraints,
                expression=col.expression,
                foreign_keys=col.foreign_keys,
                index=col.index,                
                nullable=col.nullable,
                primary_key=col.primary_key,
                onupdate=col.onupdate,
                default=col.default,
            )
            info[col.name] = ci
        return info
    
    @property
    def primary_key(self):
        '''Returns primary key col name.
        Notes:
            Returns first primary key where multiple primary
                keys exist (should be updated in future).
        '''
        for ci in self.schemainfo:
            if ci['primary_key']:
                return ci['name']
        return None
    
    
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
        
        if not is_sequence(cols):
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
    
    def select_chunk(self, cols=None, chunksize=1, max_rows=None, **kwargs):
        '''Performs select while querying only a subset of the results at a time.
        Args:
            cols (col name(s) or sqlalchemy object(s)): columns to query
            chunksize (int): size of individual queries to be made. Will
                load this number of rows into memory before yielding.
            max_rows (int): maximum number of rows to retrieve. Because 
                the limit argument is being used internally to limit data
                to smaller chunks, use this argument instead. Internally,
                this function will load a maximum of max_rows + chunksize 
                - 1 rows into memory, but yields only max_rows.
        Yields:
            sqlalchemy result: row data - same as .select() method.
        '''
        offset = 0
        while True:
            rows = self.select(cols, offset=offset, limit=chunksize, **kwargs)
            for row in rows[:max_rows-offset]:
                yield row
            offset += len(rows)
            
            if (max_rows is not None and offset >= max_rows) or len(rows) == 0:
                break
    
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
        # takes raw query object
        if conn is not None:
            r = conn.execute(query)
        elif self._conn is not None:
            r = self._conn.execute(query)
        else:
            with self._engine.connect() as conn:
                r = conn.execute(query)
        return r
    
    
    #################### Accessor Methods ###################
    
    def col(self,name):
        '''Accesses a column object. Equivalent to table.c[name].
        Args:
            Name of column to access. Applied as subscript to 
                sqlalchemy columns object.
        '''
        return self._table.c[name]
    
    def __getitem__(self, colname):
        '''Accesses a column object by calling .col().'''
        return self.col(colname)
        
    @property
    def table(self):
        '''Returns underlying sqlalchemy table object for manual manipulation.
        '''
        return self._table
    
    @property
    def tabname(self):
        '''Gets name of table for this connection.'''
        return self._tabname
    
    
    #################### Bootstrapping Methods ###################    
    
    def select_bootstrap(self, *args, **kwargs):
        ''' Performs select statement by bootstrapping output.
        Notes:
            This is a simple wrapper over .select_bootstrap_iter(),
                simply casting to a list before returning.
        Args:
            *args: passed to .select_bootstrap_iter() method.
            **kwargs: passed to .select_bootstrap_iter() method.
        Returns:
            list: result rows
        '''
        return list(self.select_bootstrap_iter(*args, **kwargs))
    
    def select_bootstrap_iter(self, cols=None, nsamp=None, where=None, idcol=None, whrstr=None, **kwargs):
        '''Bootstrap (sample with replacement) from database.
        Notes:
            This should be used in cases where the order of returned elements
                does not matter. It works internally by selecting primary key
                (idcol), sampling with replacement using python, and then performing
                select queries where idcol in (selected ids). Number of queries varies
                by the maximum count of ids which were sampled.
        Args:
            cols (sqlalchemy column names or objects): passed directly to 
                .select().
            nsamp (int): number of rows to sample with replacement.
            where (sqlalchemy condition): where criteria.
            whrstr (str): SQL command to conditionally select
            idcol (col name or object): Must be unique id assigned to each
                column. Extracts first primary key by default.
        Yields:
            sqlalchemy row objects: bootstrapped rows (order not gauranteed).
        '''
        if idcol is None:
            idcol = self.primary_key
            if idcol is None:
                raise ValueError('A primary key must exist or unique column '
                    'specified in "key" param to use bootstrapping.')
        if nsamp == None:
            nsamp = self.count()
        
        idwaves = self._bs_sampids(nsamp, idcol, where=where)
        results = list()
        for idwave in idwaves:
            for row in self.select(cols, where=self[idcol].in_(idwave), **kwargs):
                yield row
                
            
    def _bs_sampids(self,nsamp,idcol,**kwargs):
        ids = self.select(self[idcol], **kwargs) # includes WHERE clause args
        cts = collections.Counter(random.choices(ids,k=nsamp))
        
        idwaves = list()
        for i in range(max(cts.values())):
            ids = [idx for idx,ct in cts.items() if ct > i]
            idwaves.append(ids)
        return idwaves

    

coltype_error_str = ('Provided column schema must '
                    'be a two-tuple (colname, coltype), three-tuple '
                    '(colname,coltype,{sqlalchemy type data}), or '
                    'four-tuple (colname, coltype, sqlalchemy type data, '
                    '{sqlalchemy column arguments}).')
    

def is_sequence(obj):
    return isinstance(obj, list) or isinstance(obj,set) or isinstance(obj,tuple)


