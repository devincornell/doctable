
import random
import sqlalchemy
from time import time

import sys
sys.path.append('..')
from doctable import DocTable2, func, op

class MyDocuments(DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False, unique=True)),
        ('age','integer'),
        ('description','subdocs'),
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
    Nsent,sentlen = 50000,10
    for i in range(N):
        sents = [[str(i) for i in range(sentlen)] for _ in range(Nsent)]
        md.insert({'name':'user_'+str(i), 'age':random.random(),'description':sents})
    print(md) # <DocTable2::mydocuments ct: 5>
    
    print(len(md.select_first(md['description'])))
    #print(md.select_first())
    
    # this will make a select statement to sents on every iteration so that
    # the sql engine doesn't queue multiple objects into memory at once. This
    # is less useful for sents unless there is a large number of sents per doc
    # and memory is limited.
    st = time()
    print('running select_iter (one call per iter)')
    for row in md.select_iter():
        args = (row['name'],len(row['description']))
        print('user {} has a description of {} sentences.'.format(*args))
    print('took {} sec.\n'.format(time()-st))
    
    # makes a single call to teh subdoc table to load sents into memory
    st = time()
    print('running select')
    for row in md.select():
        args = (row['name'],len(row['description']))
        print('user {} has a description of {} sentences.'.format(*args))
    print('took {} sec.\n'.format(time()-st))
