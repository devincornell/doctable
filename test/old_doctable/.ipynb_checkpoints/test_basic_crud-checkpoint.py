
import os
import pytest
from random import randrange


import sys
sys.path.append('..')
from doctable import DocTable


def make_data(Nrows=1000, Nsents=5, Ntoks=3):
    names = ['sherocks {}'.format(i) for i in range(Nrows)]
    models = [[randrange(1000) for _ in range(10)] for _ in range(Nrows)]
    sents = [[[str(i) for i in range(Ntoks)] for _ in range(Nsents)] for _ in range(Nrows)]
    toks = [[str(i) for i in range(Ntoks)] for _ in range(Nrows)]
    
    cols = ('id integer PRIMARY KEY AUTOINCREMENT ', 'name VARCHAR', 'model blob', 'sents sentences', 'toks tokens')
    dt = DocTable(cols)
    
    
    for i,name,model,sent,tok in zip(range(Nrows),names,models,sents,toks):
        dat = {
            'name':name,
            'model':model,
            'sents':sent,
            'toks':tok,
        }
        
        rid = dt.add(dat)
    
    return dt, names, models, sents, toks


def test_update():
    dt, names, models, sents, toks = make_data()
    
    r1old = next(dt.get(where={'id':1}))['name']
    r2old = next(dt.get(where={'id':2}))['name']
    r3old = next(dt.get(where={'id':3}))['name']
    
    dt.update({'name':'hat'}, where={'id':2})
    
    assert(next(dt.get(where={'id':1}))['name'] == r1old)
    assert(next(dt.get(where={'id':2}))['name'] == 'hat')
    assert(next(dt.get(where={'id':3}))['name'] == r3old)
    
    print(dt.getdf(sel=['name','id'], where={'id':(1,2,3,)}))
    
    
def test_delete():
    dt, names, models, sents, toks = make_data()
    
    V = 5
    ids = list(dt.get(sel='id'))
    Nshouldremain = sum([i <= V for i in ids])
    
    dt.delete({'id':{'>':V,}})
    
    Nremain = dt.num_rows()
    
    print(Nremain, Nshouldremain)
    assert(Nremain == Nshouldremain)
    
    dt.delete_all()
    assert(dt.num_rows() == 0)
    
    
    

    
def test_add():
    # get populated database
    dt, names, models, sents, toks = make_data()
        
    for row,name,model,sent,tok in zip(dt.get(), names,models,sents,toks):
        assert(row['name'] == name)
        assert(row['model'] == model)
        assert(row['sents'] == sent)
        assert(row['toks'] == tok)
    assert(dt.num_rows() == len(names))
    
def test_addmany():
    dt, names, models, sents, toks = make_data()
    
    data = list(zip(names,models,sents,toks))
    
    dt.delete_all()
    dt.addmany(data, cols=('name', 'model', 'sents', 'toks'))
    assert(dt.num_rows() == len(names))
    
    dt.delete_all()
    dt.addmany(list(zip(names,models)),cols=('name','model'))
    assert(dt.num_rows() == len(names))
    
    with pytest.raises(ValueError):
        dt.addmany(list(zip(names,models)),cols=('namessss','model'))
    
 
def test_get():
    
    dt, names, models, sents, toks = make_data()
    ids = list(dt.get(sel='id'))
    
    alldat = list(dt.get())
    assert(dt.num_rows() == len(alldat))
    assert(len(dt.columns) == len(alldat[0]))
    
    V = 5
    Nshouldsel = sum([i < V-1 and i > V+1 for i in ids])
    Nsel = len(list(dt.get(where={'id':{'>':V+1,'<':V-1}})))
    print(Nsel)
    assert(Nshouldsel == Nsel)
    
    V = 8
    Nshouldsel = sum([i < V-1 or i > V+1 for i in ids])
    Nsel = len(list(dt.get(where={'id':{'or':({'>':V+1},{'<':V-1})}})))
    print(Nsel)
    assert(Nshouldsel == Nsel)
    
    # check out conditional with OR statement
    V = 9
    Nshouldsel = sum([i < V-1 or i > V+1 for i in ids])
    whrstr = 'id < "{}" OR id > "{}"'.format(V-1,V+1)
    Nsel = len(list(dt.get(where=whrstr)))
    print(Nsel)
    assert(Nshouldsel == Nsel)
    
    # make sure limit param words
    V = 7
    Nsel = len(list(dt.get(limit=V)))
    print(Nsel)
    assert(V == Nsel)
    
    # asdict=False doesn't return a dict
    row = next(dt.get(limit=1,asdict=False))
    print(type(row))
    assert(not isinstance(row,dict))
    
    # multiple column select gives dict (even when selecting only one col)
    row = next(dt.get(sel=['id',], limit=1))
    print(type(row))
    assert(isinstance(row,dict))
    
    # single column select gives simple list
    row = next(dt.get(sel='id', limit=1))
    print(type(row))
    assert(isinstance(row,int))
    
    # blob object is converted appropriately
    row = next(dt.get(limit=1))
    assert(isinstance(row['name'],str))
    assert(isinstance(row['model'],list))
    assert(isinstance(row['toks'],list))
    assert(isinstance(row['toks'][0],str))
    assert(isinstance(row['sents'],list))
    assert(isinstance(row['sents'][0],list))
    assert(isinstance(row['sents'][0][0],str))
    
    
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
    test_addmany()
    #test_add_many()
    