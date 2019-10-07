
import random
import sqlalchemy
from time import time

import sys
sys.path.append('..')
import doctable as dt

class DocsWithSents(dt.DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False, unique=True)),
        ('age','float'),
    )
    
    senttable = 'docsents'
    fkcols = (['fkid'],['{}.id'.format(tabname)])
    sentschema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('fkid','integer'),
        (fkcols,'foreignkey_constraint',dict(),dict(onupdate="CASCADE", ondelete="CASCADE")),
        ('sent','subdocs'),
    )
    
    def __init__(self, fname, verbose=False):
        super().__init__(
            self.schema, 
            tabname=self.tabname, 
            fname=fname, 
            verbose=verbose,
        )
        
        self.sentdt = dt.DocTable2(
            schema=self.sentschema,
            tabname=self.senttable,
            fname=fname,
            persistent_conn=False,
            new_db=False,
        )
        
    def insert_single(row,sents,*args,**kwargs):
        newid = self.next_id()
        r = self.insert(row)
        for sent in sents:
            self.sentdt.insert({'fkid':newid,'sent':sent})
    
    
    
if __name__ == '__main__':
    
    N = 5
    
    # insert one at a time
    md = DocsWithSents('tmpdump.db',verbose=True)
    Nsent,sentlen = 5,10
    for i in range(N):
        sents = [[str(i) for i in range(sentlen)] for _ in range(Nsent)]
        dat = {'name':'user_'+str(i), 'age':random.random()}
        md.insert(dat,sents)
    print(md) # <DocTable2::mydocuments ct: 5>
    