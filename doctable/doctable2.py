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

from .coltypes import TokensType, SubdocsType

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
        'pickle':sa.PickleType,
        'smallinteger':sa.SmallInteger,
        'string':sa.String,
        'text':sa.Text,
        'time':sa.Time,
        'unicode':sa.Unicode,
        'unicodetext':sa.UnicodeText,
        'tokens':TokensType, # custom datatype
        'subdocs':SubdocsType, # custom datatype
    }
    
    _constraint_map = {
        'unique_constraint': sa.UniqueConstraint,
        'check_constraint': sa.CheckConstraint,
        'primarykey_constraint': sa.PrimaryKeyConstraint,
        'foreignkey_constraint': sa.ForeignKeyConstraint,
        'index': sa.Index,
    }
    _valid_types = list(_constraint_map.keys()) + list(_type_map.keys())
    
    def __init__(self, schema=None, tabname='_documents_', fname=':memory:', engine='sqlite', persistent_conn=True, verbose=False, new_db=True):
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
        '''
        
        # in cases where user did not want to create new db but a db does not 
        # exist
        if fname != ':memory:' and not os.path.exists(fname) and not new_db:
            raise ValueError('new_db is set to true and the database does not '
                             'exist yet.')
        
        # separate tables for custom data types and main table
        self.tabname = tabname
        self.verbose = verbose
        
        self._engine = sa.create_engine('{}:///{}'.format(engine,fname))
        self._schema = schema
        
        # make table if needed
        self._metadata = sa.MetaData()
        if self._schema is not None:
            columns = self._parse_column_schema(schema)
            self._table = sa.Table(self.tabname, self._metadata, *columns)
            self._metadata.create_all(self._engine)
        else:
            self._table = sa.Table(self.tabname, self._metadata, 
                                   autoload=True, autoload_with=self._engine)
        
        # bind .min(), .max(), and .count() to col objects themselves.
        self._bind_functions()
            
        # connect with database engine
        if persistent_conn:
            self._conn = self._engine.connect()
        else:
            self._conn = None
    
    def __delete__(self):
        self.close_conn()
            
    def __str__(self):
        return '<DocTable2::{} ct: {}>'.format(self.tabname, self.count())
    
    def close_conn(self):
        if self._conn is not None:
            self._conn.close()
        self._conn = None
        
        
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
        '''Maps typstr with an sqlalchemy data type (or doctable custom type).
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
    
    def count(self,where=None, **kwargs):
        '''Count number of rows which match where condition.'''
        cter = func.count(self._table)
        ct = self.select_first(cter,where=where, **kwargs)
        return ct
    
    def next_id(self, idcol='id', **kwargs):
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
        Examples:
            some info here: 
            https://docs.sqlalchemy.org/en/13/core/metadata.html
            
            c = db.columns['id']
            c.type, c.name, c.
        '''
        return self._table.c
    
    @property
    def schemainfo(self):
        '''Get info about each column as a dictionary.
        Returns:
            dict<dict>: info about each column. Selected by
                hand, so feel free to add/remove some info.
        '''
        inspector = sa.inspect(self._engine)
        return inspector.get_columns(self.tabname)
    
    def schemainfo_long(self):
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
            Not sure of the behavior in case where multiple primary
                keys exist.
        '''
        for cn,ci in self.schemainfo.items():
            if ci['primary_key']:
                return cn
        return None
    
    
    ################# INSERT METHODS ##################
    
    def insert(self, rowdat, ifnotunique='fail', **kwargs):
        '''Insert a row.
        Args:
            rowdat (list<dict> or dict): row data to insert.
            ifnotunique: way to handle inserted data if it breaks
                a table constraint. Choose from FAIL, IGNORE, REPLACE.
        Returns:
            sqlalchemy query result object
        '''
        q = sa.sql.insert(self._table, rowdat)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        r = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    ################# SELECT METHODS ##################
    
    def select_first(self, *args, **kwargs):
        '''Perform regular select query returning only the first result.
        '''
        result = self.select(*args, limit=1, **kwargs)
        if len(result) == 0:
            raise LookupError('No results were returned. Needed to error '
                'so this result wasn not confused with case where actual '
                'result is None. If not sure about result, use regular '
                '.select() method with limit=1.')
        return result[0]
    
    def select_df(self, cols=None, *args, **kwargs):
        '''Select returning dataframe.'''
        
        if not is_sequence(cols) and cols is not None:
            raise TypeError('col argument should be multiple columns. '
                'For single column, use .select_series().')
        
        sel = self.select(cols, *args, **kwargs)
        rows = [dict(r) for r in sel]
        return pd.DataFrame(rows)
    
    def select_series(self, col, *args, **kwargs):
        '''Select returning pandas Series.
        '''
        if is_sequence(col):
            raise TypeError('col argument should be single column.')
        
        sel = self.select(col, *args, **kwargs)
        return pd.Series(sel)
    
    def select(self, cols=None, where=None, orderby=None, groupby=None, limit=None, whrstr=None, **kwargs):
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
            clausestr (str): extra SQL clauses to be appended to sql command
            **kwargs (args): to be appended to 
        Yields:
            dictionary: row data
        '''
        return_single = False
        if cols is None:
            cols = list(self._table.columns)
        else:
            if not is_sequence(cols):
                return_single = True
                cols = [cols]
                
        # query colunmns in main table
        result = self._exec_select_query(cols,where,orderby,groupby,limit,whrstr,**kwargs)
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
                
    
                
    def _exec_select_query(self, cols, where, orderby, groupby, limit, whrstr, **kwargs):
        
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
        
        result = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return result
    
    #################### Update Methods ###################
    
    def update(self, values, where=None, **kwargs):
        '''Update row(s) assigning the provided values.
        '''
            
        # update the main column values
        q = sa.sql.update(self._table).values(values)
        if where is not None:
            q = q.where(where)
        r = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    
    #################### Delete Methods ###################
    
    def delete(self,where=None, **kwargs):
        '''Delete rows from the table that meet the where criteria.
        '''
        q = sa.sql.delete(self._table)
        if where is not None:
            q = q.where(where)
        r = self.execute(q, **kwargs)
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    ################# CRITICAL SQL METHODS ##################
    
    def execute(self, query, verbose=None, **kwargs):
        '''Execute an sql command. Called by most higher-level functions.
        Args:
            verbose (bool or None): Set verbose to override 
                instance-level verbose setting. Otherwise
                defers.
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
        '''Accesses a column object.
        '''
        return self._table.c[name]
    
    def __getitem__(self, colname):
        '''Accesses a column object by calling .col().'''
        return self.col(colname)
        
    @property
    def table(self):
        return self._table
    
    
    #################### Bootstrapping Methods ###################    
    
    def select_bootstrap(self, *args, **kwargs):
        return list(self.select_bootstrap_iter(*args, **kwargs))
    
    def select_bootstrap_iter(self, cols=None, nsamp=None, where=None, idcol=None):
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
            for row in self.select(cols, where=self[idcol].in_(idwave)):
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


