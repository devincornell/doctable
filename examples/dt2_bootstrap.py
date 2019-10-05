import random
from pprint import pprint

import sys
sys.path.append('..')
from doctable import DocTable2

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
    md = MyDocuments()
    
    # insert random docs
    N = 50
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print(md)
    
    # since count is in a list, will return as list of dicts
    s = md.count()
    print(s) # [{'count_1': 5}] ###WEIRD STUFF HERE
    
    r = md.select_bootstrap(nsamp=2)
    pprint(r)
    
    
    # prints first row
    #s = md.select(limit=1)
    #print(s) # [{'id': 1, 'name': 'user_0', 'age': 0.9698034764573769}]
    