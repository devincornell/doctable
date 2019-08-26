import collections
from time import time

# operators like and_, or_, and not_, functions like sum, min, max, etc
import sqlalchemy.sql as op
from sqlalchemy.sql import func

from sqlalchemy.sql import select
import sqlalchemy as sa

from sqlalchemy.sql import and_, or_, not_

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
    custom_types = (
        'subdoc',
        'bigblob',
    )
    fkid_colname = '_fk_special_'
    
    constraint_map = {
        'unique_constraint': sa.UniqueConstraint,
        'check_constraint': sa.CheckConstraint,
        'primarykey_constraint': sa.PrimaryKeyConstraint,
    }
    
    def __init__(self, schema, tabname='_documents_', fname=':memory:', engine='sqlite', verbose=False):
        
        # separate tables for custom data types and main table
        self.tabname = tabname
        self.tabname_subdocs = '_' + tabname + '_subdocs'
        self.tabname_bigblobs = '_' + tabname + '_bigblobs'
        self.tabname_tokens = '_' + tabname + '_tokens'
        
        self.engine = sa.create_engine('{}:///{}'.format(engine,fname), echo=verbose)
        self._parse_schema_input(schema)
        self.conn = self.engine.connect()
    
    def __delete__(self):
        if self.conn is not None:
            self.conn.close()
            
    def __str__(self):
        ct = self.select_first(func.count())
        return '<DocTable2::{} ct: {}>'.format(self.tabname, ct)
        
        
    ################# INITIALIZATION METHODS ##################
    
    def _parse_schema_input(self,schema):
        self.colnames = [c[0] for c in schema]
        columns = list()
        self.special_col_types = dict()
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
            
            if coltype in sdtypes.dtypes:
                spcol_obj = sdtypes.dtypes[coltype]
                self.special_col_types[colname] = spcol_obj
                
            else:
                if coltype in self.constraint_map: # if coltype is constraint
                    if coltype in ('check_constraint',):
                        # in this case, colname should be a constraint string (i.e. "age > 0")
                        const = self.constraint_map[coltype](colname, **colargs)
                    else:
                        if not is_sequence(colname):
                            raise ValueError('First column argument on {} should '
                                'be a sequence of columns.'.format(coltype))
                        const = self.constraint_map[coltype](*colname, **colargs)
                    columns.append(const)
                
                else: # regular column type
                    typ = self._get_sqlalchemy_type(coltype)
                    col = sa.Column(colname, typ(**coltypeargs), **colargs)
                    columns.append(col)
                
                
        self._make_tables(columns, self.special_col_types)
        
    def _get_sqlalchemy_type(self,typstr):
        if typstr not in self.type_map:
            raise ValueError('Provided column type must match '
                'one of {}.'.format(self.type_map.keys()))
        else:
            return self.type_map[typstr]
    
    def _make_tables(self, columns, special_col_types):
        self.metadata = sa.MetaData()
        
        self.fkid_col = sa.Column(self.fkid_colname, sa.Integer,unique=True)
        self.doc_table = sa.Table(self.tabname, self.metadata, 
            self.fkid_col,
            *columns,
        )
        
        bigblob_colnames = self.colnames_of_type(sdtypes.BigBlobTable)
        self.bigblob_table = sdtypes.BigBlobTable(
            self.tabname_bigblobs, 
            self.metadata, 
            bigblob_colnames,
            self.fkid_col
        )
        
        subdoc_colnames = self.colnames_of_type(sdtypes.SubdocTable)
        self.subdoc_table = sdtypes.SubdocTable(
            self.tabname_subdocs, 
            self.metadata, 
            subdoc_colnames, 
            self.fkid_col
        )
        
        self.metadata.create_all(self.engine)
        
        # record table instances for each special column
        self.special_cols = dict()
        for cn in self.colnames:
            if isinstance(cn,str):
                if cn in bigblob_colnames:
                    self.special_cols[cn] = self.bigblob_table
                if cn in subdoc_colnames:
                    self.special_cols[cn] = self.subdoc_table
            
        
    
    def colnames_of_type(self, dtype):
        type_colnames = list()
        for cn in self.colnames:
            if isinstance(cn,str) and cn in self.special_col_types:
                if self.special_col_types[cn] == dtype:
                    type_colnames.append(cn)
        return type_colnames

    
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
    
    
    
    ################# INSERT METHODS ##################
    
    def insert(self, rowdat):
        
        first_id = self._next_fk_id()
        
        # if single element, just insert it
        if isinstance(rowdat,dict):
            r = self._insert_rows(rowdat, first_id, insert=True)
            return r
            
        # if iterator, insert one at a time with multiple inserts
        elif is_iter(rowdat):
            return self._insert_iter(rowdat, first_id)
        
        # if all is in memory already (list or dict), insert all at once
        else:
            return self._insert_many(rowdat, first_id)
        
    def _insert_iter(self, rowdat, first_id):
        results = list()
        for i,row in enumerate(rowdat):
            r = self._insert_rows(row, first_id+i, insert=True)
            results.append(r)
        return results
            
    def _insert_many(self, rowdat, first_id):
        main_dat_l = list()
        spec_dat_cols = dict()
        for i,row in enumerate(rowdat):
            main_dat, spec_dat = self._insert_rows(row, first_id+i, insert=False)
            main_dat_l.append(main_dat)

            for col in spec_dat.keys():
                if col not in spec_dat_cols:
                    spec_dat_cols[col] = list()
                spec_dat_cols[col].append(spec_dat[col])

        for col, spec_dat in spec_dat_cols.items():
            self._insert_special(col, spec_dat, first_id)

        q = sa.sql.insert(self.doc_table, main_dat_l)
        r = self.execute(q)
        return r
        
    def _insert_rows(self, row, first_id, insert=True):
        '''
            Parses through rows, separating main data cols
            from special data cols to be inserted in other
            tables.
            
            if insert == True, will insert while looping through
                each row, and execute insert statement at the end.
        '''
        
        main_dat = dict()
        special_dat = dict()
        main_dat[self.fkid_colname] = first_id
        for colname,dat in row.items():
            if colname in self.special_cols:
                if insert:
                    self._insert_special(colname, (dat,), first_id)
                else:
                    special_dat[colname] = dat
            else:
                main_dat[colname] = dat
            
        if insert:
            q = sa.sql.insert(self.doc_table, main_dat)
            r = self._execute(q)
            return r
        else:
            return main_dat, special_dat
    
    def _insert_special(self, colname, col_data, first_id):
        '''
            Inserts list of col_data into appropriate table
                as per the special column yield functions.
        '''
        
        if colname in self.special_cols:
            tab = self.special_cols[colname]
            r = tab.insert(colname, col_data, first_id, self)
        else:
            raise ValueError
        
        return r
                
    def _next_fk_id(self):
        q = sa.sql.select([func.max(self.fkid_col)])
        maxi = self.execute(q).fetchone()[0]
        if maxi is None:
            return 1
        else:
            return maxi + 1
    
    
    ################# SELECT METHODS ##################
    
    def select(self, cols=None, **kwargs):
        '''Perform select query on database, 1 + 1 query per special table.
        Args:
            cols: list of columns
        
        '''
        if cols is None:
            cols = list(self.doc_table.columns) + list(self.special_cols.keys())
        else:
            if not is_sequence(cols):
                cols = [cols]
        
        # split special cols from main_cols
        colnames, main_cols, spec_colnames = self._identify_cols(cols + [self.fkid_col])
        
        # extract data from regular columns
        main_rows = list(self.select_iter(main_cols, **kwargs))
        docids = [r[self.fkid_colname] for r in main_rows]
        
        spcol_dat = dict()#{cn:dict() for cn in spec_colnames}
        for cn in spec_colnames:
            sp_tab = self.special_cols[cn]
            sp_result = sp_tab.select(cn, docids, self)
            for mr in main_rows:
                mr[cn] = sp_result[mr[self.fkid_colname]]
        
        for mr in main_rows:
            del mr[self.fkid_colname]
        
        return main_rows
    
    def select_first(self, *args, **kwargs):
        return next(self.select_iter(*args, limit=1, **kwargs))
    
    
    def select_iter(self, cols=None, where=None, orderby=None, groupby=None, limit=None):
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
            cols = list(self.doc_table.columns) + list(self.special_cols.keys())
        else:
            if not is_sequence(cols):
                return_single = True
                cols = [cols]
        
        # split special cols from main_cols
        colnames, main_cols, spec_colnames = self._identify_cols(cols + [self.fkid_col])
        
        # query colunmns in main table
        result = self._exec_select_query(main_cols,where,orderby,groupby,limit)
        
        # return results one at a time
        if len(spec_colnames) > 0: # special columns were selected
            for row in result:
                rdict = dict(row)
                docid = rdict[self.fkid_colname]
                for cn in spec_colnames:
                    sp_tab = self.special_cols[cn]
                    sp_result = sp_tab.select(cn, [docid],self)
                    rdict[cn] = sp_result[docid]
                del rdict[self.fkid_colname]
                yield rdict
        
        else: # special columns were not selected
            for row in result:
                if return_single:
                    yield row[main_cols[0]]
                else:
                    yield dict(row)

    def _identify_cols(self, cols):
        '''Separate special cols from main table columns.
        Needed so that the correct data can be sent to the correct column.
        
        Args:
            cols (list[sqlalchemy.Column] or str)
        
        '''
        colnames = list()
        spec_colnames = list()
        main_cols = list()
        already_added_fk_col = False
        for col in cols:
            
            if isinstance(col,str):
                colnames.append(col)
                spec_colnames.append(col)
                
                if not already_added_fk_col:
                    main_cols.append(self.fkid_col)
                    already_added_fk_col = True
                
            else:
                colnames.append(col.name)
                main_cols.append(col)
        
        return colnames, main_cols, spec_colnames
                
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
    


            
    def _select_special(self, colnames, doc_ids):
        '''
            Returns: Map of maps; for each document,
                maintain a map of data corresponding
                to each column.
                doc_id->col_name->col_data
        '''
        res = dict()
        for cname in colnames:
            # map: cname->data_table object
            spcol = self.special_cols[cname]
            res[cname] = spcol.select(cname, doc_ids, self)
        
        # flip from colname->docid->val to docid->colname->val.
        docid_dict = dict()
        for cname,u in res.items():
            for docid,v in u.items():
                if docid not in docid_dict:
                    docid_dict[docid] = dict()
                docid_dict[docid][cname] = v
            
        return docid_dict

    
    #################### Accessor Methods ###################
    
    def col(self,name):
        ref = self[name]
        return ref
    
    def __getitem__(self, colname):
        if colname in self.special_cols:
            return colname
        else:
            # throws error if not in table columns
            return self.doc_table.c[colname]
    
    def _subdoc(self, colname):
        ref = self.subdoc_table.c[colname]
        return ref
    
    def _bigblob(self, colname):
        ref = self.bigblob_table.c[colname]
        return ref
        
    def table(self):
        return self.doc_table
    

coltype_error_str = ('Provided column schema must '
                    'be a two-tuple (colname, coltype), three-tuple '
                    '(colname,coltype,{sqlalchemy type data}), or '
                    'four-tuple (colname, coltype, sqlalchemy type data, '
                    '{sqlalchemy column arguments}).')
    

def is_iter(obj):
    isiter = isinstance(obj, collections.Iterable)
    isinmemory = isinstance(obj,list) or isinstance(obj,set) or isinstance(obj,tuple)
    return isiter and not isinmemory

def is_sequence(obj):
    return isinstance(obj, list) or isinstance(obj,set) or isinstance(obj,tuple)


