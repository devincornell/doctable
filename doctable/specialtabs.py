
import sqlalchemy as sa

from .coltypes import TokensType

class TableBase:
    def __getitem__(self, colname):
        return self.doc_table.c[colname]
    
    def insert(self, colname, coldata, start_id, parentref):
        '''Generic code for inserting data into special column table.
            Relies on self._rows_from_coldata() to convert the input
            into special column table rows. Alternatively can be 
            overloaded.
        '''
        rows = self._rows_from_coldata(colname, coldata, start_id)
        q = sa.sql.insert(self.table, list(rows))
        r = parentref.execute(q)
        return r
    
    def _rows_from_coldata(self, colname, coldata, start_id):
        raise NotImplementedError()
        
    def select(self, colname, doc_ids, parentref):
        raise NotImplementedError()
        
    def update(self, colname, doc_ids, value, parentref):
        raise NotImplementedError()
        
        
class BigPickleTable(TableBase):

    def __init__(self, tabname, metaref, cols, foreignkey_col):
        
        colname_constraint = 'col_name in ("{}")'.format('","'.join(cols))
        self.table = sa.Table(tabname, metaref,
            sa.Column('id', sa.Integer, primary_key=True),  
            sa.Column('col_name', sa.String, sa.CheckConstraint(colname_constraint)),
            sa.Column('doc_id', sa.ForeignKey(foreignkey_col, onupdate="CASCADE", ondelete="CASCADE")),
            sa.Column('num_bytes', sa.Integer),
            sa.Column('bigpickle', sa.PickleType),
            sa.Index('idx_bigpickles0', 'col_name', 'doc_id', unique=True),
        )
    
    @staticmethod
    def _rows_from_coldata(colname, coldata, start_id):
        for i,blob in enumerate(coldata):
            doc_id = start_id + i
            row = {
                'col_name': colname,
                'doc_id': doc_id,
                'num_bytes': None,
                'bigpickle': blob,
            }
            yield row
            
    def select(self, colname, doc_ids, parentref):
        q = sa.sql.select([self.table.c['bigpickle'], self.table.c['doc_id']])
        q = q.where(self.table.c['doc_id'].in_(doc_ids))
        q = q.where(self.table.c['col_name'] == colname)
        bigpicklerows = parentref.execute(q)
        return {r['doc_id']:r['bigpickle'] for r in bigpicklerows}
    
    def update(self, colname, doc_ids, value, parentref):
        q = sa.sql.update(self.table)
        q = q.where(self.table.c['doc_id'].in_(doc_ids) & (self.table.c['col_name']==colname))
        q = q.values({'bigpickle':value,'num_bytes':None})
        r = parentref.execute(q)
        return r
            
            
class SubdocTable(TableBase):

    def __init__(self, tabname, metaref, colnames, foreignkey_col):
        
        colname_constraint = 'col_name in ("{}")'.format('","'.join(colnames))
        self.table = sa.Table(tabname, metaref,
            sa.Column('id', sa.Integer, primary_key=True),  
            sa.Column('col_name', sa.String, sa.CheckConstraint(colname_constraint)),
            sa.Column('doc_id', sa.ForeignKey(foreignkey_col, onupdate="CASCADE", ondelete="CASCADE")),
            sa.Column('order', sa.Integer),
            sa.Column('num_tokens', sa.Integer),
            sa.Column('tokens', TokensType),
            sa.Index('idx_subdocs0', 'col_name', 'doc_id', 'order', unique=True),
            sa.Index('idx_subdocs1', 'col_name', 'doc_id', unique=False),
        )
    
    @staticmethod
    def _rows_from_coldata(colname, coldata, start_id):
        for i,subdocs in enumerate(coldata):
            doc_id = start_id + i
            for j,subdoc in enumerate(subdocs):
                subdocrow = {
                    'col_name': colname,
                    'doc_id': doc_id,
                    'order': j,
                    'num_tokens': len(subdoc),
                    'tokens': subdoc,
                }
                yield subdocrow
            
            
    def select(self, colname, doc_ids, parentref):
        
        q = sa.sql.select([
            self.table.c['doc_id'],
            self.table.c['tokens'],
        ]).where(
            (self.table.c['doc_id'].in_(doc_ids)) &
            (self.table.c['col_name'] == colname)
        ).order_by(self.table.c['order'].asc())
        res = list(parentref.execute(q))
        
        # format subdocs
        subdocs = {did:list() for did in doc_ids}
        for did,tok in res:
            subdocs[did].append(tok)
        return subdocs
    
    def update(self, colname, doc_ids, value, parentref):
        # delete all sents assigned to those ids
        q = sa.sql.delete(self.table)
        q = q.where(self.table.c['doc_id'].in_(doc_ids) & (self.table.c['col_name']==colname))
        rd = parentref.execute(q)
        
        # insert sents for each of the ids
        cd = (value for _ in range(len(doc_ids)))
        r = self.insert(self, colname, coldata, doc_ids, parentref)
        
        return r
        

dtypes = {
    'bigpickle':BigPickleTable,
    'subdocs': SubdocTable,
}
