import random

import sys
sys.path.append('..')
from doctable import DocTable2, func, op

class MyDocuments(DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False)),
        ('age','integer'),
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
    md = MyDocuments('mydb2.db')
    
    N = 20
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print(md.select(func.count(name='shit')))
    print(md.select_first(func.count()))
    print(md)
    
    
