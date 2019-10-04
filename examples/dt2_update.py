
import random
import sqlalchemy
import pprint
import pandas as pd

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
    
    N = 5
    
    # insert one at a time
    md = MyDocuments()
    print(md.schema_str)
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print(md) # <DocTable2::mydocuments ct: 5>
    print(pd.DataFrame(md.select()), '\n')
    
    md.update({'name':'best_user'},where=md['name']=='user_1')
    print('updated user_1 -> best_user:')
    print(pd.DataFrame(md.select()), '\n')
    
    md.update({'age':16})
    print('updated all ages to 16:')
    print(pd.DataFrame(md.select()), '\n')
    