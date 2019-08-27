
import random
import sqlalchemy
import pprint

import sys
sys.path.append('..')
from doctable import DocTable2, func, op

class MyDocuments(DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False, unique=True)),
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
    
    N = 10
    
    # insert one at a time
    md = MyDocuments()
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print(md) # <DocTable2::mydocuments ct: 10>
    
    print('deleting now')
    Nrm = N//2
    md.delete(md['id']>Nrm)
    print(md) # <DocTable2::mydocuments ct: 5>
    
    md.delete()
    print(md) # <DocTable2::mydocuments ct: 0>