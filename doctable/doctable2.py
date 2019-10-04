import collections
from time import time
import pprint
import random

# operators like and_, or_, and not_, functions like sum, min, max, etc
import sqlalchemy.sql as op
from sqlalchemy.sql import func
import sqlalchemy as sa

from .coltypes import TokensType
from . import specialtabs as sdtypes

class DocTable2:
    type_map = {
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
    }
    
    constraint_map = {
        'unique_constraint': sa.UniqueConstraint,
        'check_constraint': sa.CheckConstraint,
        'primarykey_constraint': sa.PrimaryKeyConstraint,
    }
    
    def __init__(self, schema, tabname='_documents_', fname=':memory:', engine='sqlite', persistent_conn=True, verbose=False):
        
        # separate tables for custom data types and main table
        self.tabname = tabname
        self.persistent_conn = persistent_conn
        
        self.engine = sa.create_engine('{}:///{}'.format(engine,fname), echo=verbose)
        self.schema = schema
        self._parse_schema_input(schema)
        self.conn = self.engine.connect()
        self.next_fkid = None
    
    def __delete__(self):
        if self.conn is not None:
            self.conn.close()
            
    def __str__(self):
        return '<DocTable2::{} ct: {}>'.format(self.tabname, self.num_rows)
        
        
    ################# INITIALIZATION METHODS ##################
    
    def _parse_schema_input(self,schema):
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
            
            if not coltype in self.constraint_map: # if coltype is regular column
                typ = self._get_sqlalchemy_type(coltype)
                col = sa.Column(colname, typ(**coltypeargs), **colargs)
                columns.append(col)

            else: # column is actually a constraint (not regular column)
                if coltype in constraint_map:
                    # in this case, colname should be a constraint string (i.e. "age > 0")
                    const = self.constraint_map[coltype](colname, **colargs)
                else:
                    if not is_sequence(colname):
                        raise ValueError('First column argument on {} should '
                            'be a sequence of columns.'.format(coltype))
                    const = self.constraint_map[coltype](*colname, **colargs)
                columns.append(const)

        # actually create table
        self.metadata = sa.MetaData()
        self.table = sa.Table(self.tabname, self.metadata, *columns)
        self.metadata.create_all(self.engine)
                
    def _get_sqlalchemy_type(self,typstr):
        '''Maps typstr with an sqlalchemy data type (or doctable custom type).
        '''
        if typstr not in self.type_map:
            raise ValueError('Provided column type must match '
                'one of {}.'.format(self.type_map.keys()))
        else:
            return self.type_map[typstr]
    
    
    ################# INSERT METHODS ##################
    
    #
    def insert(self, rowdat, ifnotunique='fail'):
        '''Insert a row.
        Args:
            rowdat (list<dict> or dict): row data to insert.
            ifnotunique: way to handle inserted data if it breaks
                a table constraint. Choose from FAIL, IGNORE, REPLACE.
        Returns:
            sqlalchemy query result object
        '''
        q = sa.sql.insert(self.table, rowdat)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        r = self.execute(q)
    
    
    ################# SELECT METHODS ##################
    
    def select_first(self, *args, **kwargs):
        '''Perform regular select query returning only the first result.'''
        return self.select(*args, limit=1, **kwargs)[0]
    
    def select(self, cols=None, where=None, orderby=None, groupby=None, limit=None):
        '''Perform select query, yield result for each row.
        
        Description: Because output must be iterable, returns special column results 
            by performing one query per row. Can be inefficient for many smaller 
            special data information.
        
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where: sqlalchemy where object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
        Yields:
            dictionary: row data
        '''
        return_single = False
        if cols is None:
            cols = list(self.table.columns)
        else:
            if not is_sequence(cols):
                return_single = True
                cols = [cols]
                
        # query colunmns in main table
        result = self._exec_select_query(cols,where,orderby,groupby,limit)
        
        # return output as list
        if return_single:
            return [r[0] for r in result]
        else:
            return [dict(r) for r in result]
    
            
    def old_select(self, cols=None, **kwargs):
        '''Perform select query on database, 1 + 1 query per special table.
        Args:
            cols: list of columns
        '''
        return_single = False
        if cols is None:
            cols = list(self.table.columns) + list(self.special_cols.keys())
        else:
            if not is_sequence(cols):
                return_single = True
                cols = [cols]
        
        # extract data from regular columns
        main_rows = list(self.select_iter(main_cols, **kwargs))
        
        for row in result:
            if return_single:
                yield row[main_cols[0]]
            else:
                yield dict(row)
                
    def _exec_select_query(self, cols, where, orderby, groupby, limit):
        
        q = sa.sql.select(cols)
        
        if where is not None:
            q = q.where(where)
        if orderby is not None:
            q = q.order_by(orderby)
        if groupby is not None:
            q = q.groupby(orderby)
        if limit is not None:
            q = q.limit(limit)
        
        result = self.execute(q)
        
        return result
    


    
    #################### Update Methods ###################
    
    def update(self,values,where=None):
        '''Update row(s) assigning the provided values.
        '''
            
        # update the main column values
        q = sa.sql.update(self.table).values(values)
        if where is not None:
            q = q.where(where)
        r = self.execute(q)
            
        # update special columns
        if len(spcols) > 0:
            q = self.select(self.fkid_col,where=where)
            ids = self.execute(q)
            
            for cn in spcols:
                sp_tab = self.special_cols[cn]
                sp_result = sp_tab.update(cn, docids, self)
            
        return r
    
    
    #################### Delete Methods ###################
    
    def delete(self,where=None):
        
        q = sa.sql.delete(self.table)
        if where is not None:
            q = q.where(where)
        r = self.execute(q)
        return r
    
    ################# CRITICAL SQL METHODS ##################
    
    def execute(self, query):
        # try to parse
        result = self._execute(query)
        return result
        
    def _execute(self, query):
        # takes raw query object
        if self.conn is not None:
            r = self.conn.execute(query)
        else:
            with self.engine.connect() as conn:
                r = conn.execute(query)
        return r
    
    
    #################### Accessor Methods ###################
    
    def col(self,name):
        ref = self[name]
        return ref
    
    def __getitem__(self, colname):

        return self.table.c[colname]
        
    @property
    def num_rows(self):
        return self.select_first(func.count())
    
    @property
    def schema_str(self):
        return pprint.pformat(self.schema)
    
    
    #################### Bootstrapping Methods ###################
    
    
    def select_bootstrap(self, cols=None, nsamp=None, where=None):
        idwaves = self._bs_sampids(nsamp, where=where)
        results = list()
        for idwave in idwaves:
            results += self.select(cols, where=self.fkid_col.in_(idwave))
        return results
    
    
    def select_bootstrap_iter(self, cols=None, nsamp=None, where=None):
        idwaves = self._bs_sampids(nsamp, where=where)
        results = list()
        for idwave in idwaves:
            for row in self.select_iter(cols, where=self.fkid_col.in_(idwave)):
                yield row
                
            
    def _bs_sampids(self,nsamp,**kwargs):
        if nsamp == None:
            nsamp = self.num_rows
        print(kwargs)
        
        ids = self.select(self.fkid_col, **kwargs) # includes WHERE clause args
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


