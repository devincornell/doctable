import random
from pprint import pprint

import sys
sys.path.append('..')
from doctable import DocTable2

class MyDocuments(DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False, unique=True)),
        ('age','integer',dict(comment='Hahaha this is my comment.')),
    )
    
    def __init__(self, fname=':memory:', engine='sqlite', verbose=False):
        super().__init__(
            self.schema, 
            tabname=self.tabname, 
            fname=fname,
            engine=engine,
            verbose=verbose,
        )
    
    
    
if __name__ == '__main__':
    md = MyDocuments()
    print('next id:', md.next_id())
    # insert random docs
    N = 50
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print(md)
        
    print(md.count(md['age']>0.5))
        
    print('next id:', md.next_id())
    
    
    pprint(md.schema)
        
    