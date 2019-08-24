
import sqlalchemy as sa

from coltypes import TokensType

class TableBase:
    def __getitem__(self, colname):
        return self.doc_table.c[colname]
    
    def insert(self, colname, coldata, start_id, parentref):
        rows = self._rows_from_coldata(colname, coldata, start_id)
        q = sa.sql.insert(self.table, list(rows))
        r = parentref.execute(q)
        return r
    
    def _rows_from_coldata(self, colname, coldata, start_id):
        raise NotImplementedError
        
        
        
        
class BigBlobTable(TableBase):

    def __init__(self, tabname, metaref, cols, foreignkey_col):
        
        colname_constraint = 'col_name in ("{}")'.format('","'.join(cols))
        self.table = sa.Table(tabname, metaref,
            sa.Column('id', sa.Integer, primary_key=True),  
            sa.Column('col_name', sa.String, sa.CheckConstraint(colname_constraint)),
            sa.Column('doc_id', sa.ForeignKey(foreignkey_col, onupdate="CASCADE", ondelete="CASCADE")),
            sa.Column('num_bytes', sa.Integer),
            sa.Column('bigblob', sa.PickleType),
            sa.Index('idx_bigblobs0', 'col_name', 'doc_id', unique=True),
        )
    
    @staticmethod
    def _rows_from_coldata(colname, coldata, start_id):
        for i,blob in enumerate(coldata):
            doc_id = start_id + i
            row = {
                'col_name': colname,
                'doc_id': doc_id,
                'num_bytes': None,
                'bigblob': blob,
            }
            yield row
            
    def select(self, colname, doc_ids, parentref):
        q = sa.sql.select([self.table.c['bigblob'], self.table.c['doc_id']])
        q = q.where(self.table.c['doc_id'].in_(doc_ids))
        q = q.where(self.table.c['col_name'] == colname)
        bigblobrows = parentref.execute(q)
        return {r['doc_id']:r['bigblob'] for r in bigblobrows}
        
            
            
            
            
            
class SentTable(TableBase):

    def __init__(self, tabname, metaref, colnames, foreignkey_col):
        
        colname_constraint = 'col_name in ("{}")'.format('","'.join(colnames))
        self.table = sa.Table(tabname, metaref,
            sa.Column('id', sa.Integer, primary_key=True),  
            sa.Column('col_name', sa.String, sa.CheckConstraint(colname_constraint)),
            sa.Column('doc_id', sa.ForeignKey(foreignkey_col, onupdate="CASCADE", ondelete="CASCADE")),
            sa.Column('order', sa.Integer),
            sa.Column('num_tokens', sa.Integer),
            sa.Column('tokens', TokensType),
            sa.Index('idx_sents0', 'col_name', 'doc_id', 'order', unique=True),
            sa.Index('idx_sents1', 'col_name', 'doc_id', unique=False),
        )
    
    @staticmethod
    def _rows_from_coldata(colname, coldata, start_id):
        for i,sents in enumerate(coldata):
            doc_id = start_id + i
            for j,sent in enumerate(sents):
                sentrow = {
                    'col_name': colname,
                    'doc_id': doc_id,
                    'order': j,
                    'num_tokens': len(sent),
                    'tokens': sent,
                }
                yield sentrow
            
            
    def select(self, colname, doc_ids, parentref):
        q = sa.sql.select([self.table.c['tokens'], self.table.c['doc_id']])
        q = q.where(self.table.c['doc_id'].in_(doc_ids))
        q = q.where(self.table.c['col_name'] == colname)
        bigblobrows = parentref.execute(q)
        return {r['doc_id']:r['tokens'] for r in bigblobrows}
        

dtypes = {
    'bigblob':BigBlobTable,
    'sentences': SentTable,
}
