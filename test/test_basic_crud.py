
import os
import pytest
from random import randrange


import sys
sys.path.append('..')
from doctable import DocTable

    
        
def test_add():
    cols = ('id integer PRIMARY KEY AUTOINCREMENT ', 'name VARCHAR', 'model blob', 'sents sentences', 'toks tokens')
    dt = DocTable(cols)
    
    Nrows = 1000
    Nsents = 5
    Ntoks = 3
    names = ['sherocks {}'.format(i) for i in range(Nrows)]
    models = [[randrange(1000) for _ in range(10)] for _ in range(Nrows)]
    sents = [[[str(i) for i in range(Ntoks)] for _ in range(Nsents)] for _ in range(Nrows)]
    toks = [[str(i) for i in range(Ntoks)] for _ in range(Nrows)]
    
    for name,model,sent,tok in zip(names,models,sents,toks):
        dat = {
            'name':name,
            'model':model,
            'sents':sent,
            'toks':tok,
        }
        
        dt.add(dat)
        
    for row,name,model,sent,tok in zip(dt.get(verbose=True), names,models,sents,toks):
        assert(row['name'] == name)
        assert(row['model'] == model)
        assert(row['sents'] == sent)
        assert(row['toks'] == tok)
    
    
def test_checkschema():
    tmpdbname = '_tmp.db'
    
    cols1 = ('id integer PRIMARY KEY AUTOINCREMENT ', 'name VARCHAR', 'model blob', 'sents sentences', 'toks tokens')
    dt1 = DocTable(cols1,tmpdbname)
    
    cols2 = ('id integer PRIMARY KEY AUTOINCREMENT ', 'name varchar', 'model BLOB', 'sents sentences', 'toks tokens')
    dt2 = DocTable(cols2,tmpdbname)
       
    cols3 = ('whoops integer PRIMARY KEY AUTOINCREMENT ', 'name VARCHAR', 'model blob', 'sents sentences', 'toks tokens')
    with pytest.raises(ValueError) as err:
        dt3 = DocTable(cols3,tmpdbname)
        
    cols4 = ('id blob PRIMARY KEY AUTOINCREMENT ', 'name VARCHAR', 'model blob', 'sents sentences', 'toks tokens')
    with pytest.raises(ValueError):
        dt4 = DocTable(cols4,tmpdbname)
        
    
    
if __name__ == '__main__':
    test_add()
    #test_add_many()
    