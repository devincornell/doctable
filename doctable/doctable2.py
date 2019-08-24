import collections
#from sqlalchemy import create_engine
#from sqlalchemy.ext.declarative import declarative_base
#from sqlalchemy import Table, MetaData, Column, Integer, String, Boolean, ForeignKey, func
from sqlalchemy.orm import sessionmaker
from time import time
from sqlalchemy.sql import select
from coltypes import TokensType
import sqlalchemy as sa
from coltypes import TokensType
import sys

#from special_tables import dtype_objects as 
import special_dtypes as sdtypes

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
    }
    custom_types = (
        #'tokens',
        'sentences',
        'bigblob',
    )
    fkid_colname = '_fk_special_'
    
    def __init__(self, schema, tabname='_documents_', fname=':memory:', engine='sqlite', verbose=False):
        
        # separate tables for custom data types and main table
        self.tabname = tabname
        self.tabname_sents = '_' + tabname + '_sents'
        self.tabname_bigblobs = '_' + tabname + '_bigblobs'
        self.tabname_tokens = '_' + tabname + '_tokens'
        
        self.engine = sa.create_engine('{}:///{}'.format(engine,fname), echo=verbose)
        self._parse_schema_input(schema)
        self.conn = self.engine.connect()
    
    def __delete__(self):
        if self.conn is not None:
            self.conn.close()     
        
        
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
        
        sent_colnames = self.colnames_of_type(sdtypes.SentTable)
        self.sent_table = sdtypes.SentTable(
            self.tabname_sents, 
            self.metadata, 
            sent_colnames, 
            self.fkid_col
        )
        
        self.metadata.create_all(self.engine)
        
        # record table instances for each special column
        self.special_cols = dict()
        for cn in self.colnames:
            if cn in bigblob_colnames:
                self.special_cols[cn] = self.bigblob_table
            if cn in sent_colnames:
                self.special_cols[cn] = self.sent_table
            
        
        
    def colnames_of_type(self, dtype):
        type_colnames = list()
        for cn in self.colnames:
            if cn in self.special_col_types:
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
        q = sa.sql.select([self.max(self.fkid_col)])
        maxi = self.execute(q).fetchone()[0]
        if maxi is None:
            return 1
        else:
            return maxi + 1
    
    
    ################# SELECT METHODS ##################
    
    def select(self, cols=None, where=None, orderby=None, groupby=None, limit=None, asdict=True, iter_data=True):
        
        colnames, main_cols, spec_colnames = self._identify_cols(cols)
        
        # query colunmns in main table
        result = self._select_query(main_cols,where,orderby,groupby,limit)
        
        # if data_queries, query data as iterate through main table results
        if iter_data:
            for row in result:
                
                if self.fkid_colname in row:
                    doc_id = row[self.fkid_colname]
                    spec_results = self._select_special(spec_colnames, (doc_id,))
                    out_row = self._parse_row_output(colnames, row, asdict, spec_results[doc_id])
                else:
                    out_row = self._parse_row_output(colnames, row, asdict)
                yield out_row
    
    def _parse_row_output(self, colnames, main_row, asdict, spec_col_row={}):
        '''
        
        '''
        if len(spec_col_row) == 0:
            if asdict:
                return {cn:d for cn,d in zip(colnames, main_row)}
            else:
                return main_row
        else:
            if asdict:
                rowdict = dict()
                i = 0
                for cn in colnames:
                    if cn in spec_col_row:
                        rowdict[cn] = spec_col_row[cn]
                    elif cn != self.fkid_colname:
                        rowdict[cn] = main_row[i]
                        i += 1
                return rowdict
            else:
                row = list()
                i = 0
                for cn in colnames:
                    if cn in spec_col_row:
                        row.append(spec_col_row[cn])
                    else:
                        row.append(main_row[i])
                        i += 1
                return row

            
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
        
    def _identify_cols(self, cols):
        if cols is None:
            cols = list(self.doc_table.columns) + list(self.special_cols.keys())
        else:
            if not is_sequence(cols):
                cols = [cols]
        
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
        
    def _select_query(self, cols, where, orderby, groupby, limit):
        
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
    
    
    
        
    def _select_format_row(self, row, asdict, spec_cols=[]):
        '''
            Parse a single output row. If spec_cols is empty, don't
            query any special column tables. If it is a list of 
            special column names, query for the individual rows.
        '''
        colnames = list(row.keys())
        
        for col in spec_cols:
            if col in self.sent_cols:
                row[col] = self._get_sents(col, [row[self.fk_col]])
            elif col in self.bigblob_cols:
                row[col] = self._get_bigblobs(col, [row[self.fk_col]])
            else:
                raise ValueError
        
        if len(row) == 1:
            return self._parse_select(colnames[0], row[0])
            
        elif asdict:
            colvals = zip(row.keys(), row)
            return {c:self._parse_select(c,v) for c,v in colvals}
        else:
            return row
    
    def _get_sents(self, colname, doc_ids):
        if col not in self.sent_cols:
            raise KeyError('col is not of "sentences" type.')
            
        q = sa.sql.select(self._sent['tokens'])
        q = q.where(self._sent['doc_id'].in_(doc_ids))
        q = q.where(self._sent['col_name'] == colname)
        q = q.order_by(self._sent['order'])
        sentrows = self.execute(q)
        return [r['tokens'] for r in sentrows]
    
    def _get_bigblobs(self, colname, doc_ids):
        if col not in self.bigblob_cols:
            raise KeyError('col is not of "bigblob" type.')
            
        q = sa.sql.select(self._bigblob['bigblob'])
        q = q.where(self._sent['doc_id'].in_(doc_ids))
        q = q.where(self._sent['col_name'] == colname)
        bigblobrow = self.execute(q).fetchone()
        return bigblobrow['bigblob']
        
    def _parse_select(self, col, val):
        '''
            If needs parsing, passes to specific custom column parser.
        '''
        if col in self.sent_cols:
            return self._parse_select_sents(col, val)
        else:
            return val
        
    def _parse_select_sents(self, col, doc_ids):
        '''
            Gets tokens from sentences with doc_ids sorted by order.
        '''
        if not is_sequence(doc_ids):
            doc_ids = (doc_ids,)
        
        iscolname = self._sent('col_name') == col
        inids = self._sent('doc_id').in_(doc_ids)
        
        sel = sa.sql.select([self._sent('tokens')])
        sel = sel.where(sa.and_(iscolname,inids))
        sel = sel.order_by(self._sent('doc_id'),self._sent('order'))
        res = self.execute(sel)
        return (r[0] for r in res)
    
    
    #################### Accessor Methods ###################
    
    def col(self,name):
        ref = self[name]
        return ref
    
    def __getitem__(self, colname):
        if colname in self.special_cols:
            return colname
        else:
            return self.doc_table.c[colname]
    
    def _sent(self, colname):
        ref = self.sent_table.c[colname]
        return ref
    
    def _bigblob(self, colname):
        ref = self.bigblob_table.c[colname]
        return ref
        
    def table(self):
        return self.doc_table
    
    
    #################### SQLAlchemy Static-Access Methods ###################
    
    @staticmethod
    def or_(arg):
        return sa.or_(arg)
    
    @staticmethod
    def and_(arg):
        return sa.and_(arg)
    
    @staticmethod
    def max(arg):
        return sa.sql.expression.func.max(arg)
    
    @staticmethod
    def min(arg):
        return sa.sql.expression.func.min(arg)

    
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
    
'''
For bootstrapping sentences. First create an entry
for each sentence to be bootstrapped (after identifying
docs that meet a "where" criteria), then assign them each
a unique id (bs_id) which can be selected using the 
SQL random() function for random sampling with replacement.
'''

