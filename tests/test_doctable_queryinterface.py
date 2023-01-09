import random
from time import time
import datetime

import sys
sys.path.append('..')
import doctable
import sqlalchemy
import pytest

@doctable.schema
class MyObj:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    age: int = doctable.Col()
    added: datetime.datetime = doctable.AddedCol()
    updated: datetime.datetime = doctable.UpdatedCol()



    
def test_select_iter_basic():
    tab = doctable.DocTable(target=':memory:', schema=MyObj)
    
    num_test_objs = 100
    test_objs = [MyObj(name=f'User{i//2}', age=i) for i in range(num_test_objs)]
    test_dicts = [o.as_dict() for o in test_objs]
    
    
    
    #with pytest.raises(doctable.ObjectToDictCovnersionFailedError):
    #    tab.q.insert_single(o.as_dict())

    with pytest.raises(TypeError):
        tab.q.insert_single(test_objs)
        tab.q.insert_single(test_dicts)
        tab.q.insert_single_raw(test_objs)
        tab.q.insert_single_raw(test_dicts)

    tab.q.insert_multi(test_objs)
    tab.q.insert_multi_raw(test_dicts)
    tab.q.insert_multi_raw([])
    tab.q.insert_multi([])

    with pytest.raises(doctable.ObjectToDictCovnersionFailedError):
        tab.q.insert_multi(test_dicts)
        
    with pytest.raises(TypeError):
        tab.q.insert_multi(None)
        tab.q.insert_multi_raw(None)
        tab.q.insert_multi_raw(test_objs)

    for o in test_objs:
        tab.q.insert_single(o)

        with pytest.raises(doctable.ObjectToDictCovnersionFailedError):
            tab.q.insert_single(o.as_dict())

        tab.q.insert_single_raw(o.as_dict())
        
        with pytest.raises(doctable.sqlalchemy.exc.ArgumentError):
            tab.q.insert_single_raw(o)

        with pytest.raises(TypeError):
            tab.q.insert_multi(o)
            tab.q.insert_multi_raw(o)
            tab.q.insert_multi(o.as_dict())
            tab.q.insert_multi_raw(o.as_dict())

    assert(tab.q.count()>0)

    with pytest.raises(ValueError):
        tab.q.delete()

    tab.q.delete(delete_all=True)
    assert(tab.q.count()==0)

    tab.q.insert_multi(test_objs)
    assert(tab.q.count() == len(test_objs))
    for o,dbo in zip(test_objs, tab.q.select()):
        assert(o.name == dbo.name)
        assert(o.age == dbo.age)
        assert(dbo.added is not None)
        assert(dbo.updated is not None)
        assert(dbo.id is not None)

    for o,dbo in zip(test_dicts, tab.q.select_raw()):
        assert(o['name'] == dbo['name'])
        assert(o['age'] == dbo['age'])
        assert(dbo['added'] is not None)
        assert(dbo['updated'] is not None)
        assert(dbo['id'] is not None)

    
    tab.q.delete(delete_all=True)
    tab.q.insert_multi_raw(test_dicts)
    assert(tab.q.count() == len(test_objs))
    for o,dbo in zip(test_objs, tab.q.select()):
        assert(o.name == dbo.name)
        assert(o.age == dbo.age)
        assert(dbo.added is not None)
        assert(dbo.updated is not None)
        assert(dbo.id is not None)

    for o,dbo in zip(test_dicts, tab.q.select_raw()):
        assert(o['name'] == dbo['name'])
        assert(o['age'] == dbo['age'])
        assert(dbo['added'] is not None)
        assert(dbo['updated'] is not None)
        assert(dbo['id'] is not None)
    
    age_sum = sum([o.age for o in test_objs])
    assert(tab.q.select_scalar(tab['age'].sum()) == age_sum)

    # try sorting by descending
    sorted_ages = tab.q.select_col(tab['age'], orderby=tab['age'].desc())
    assert(sorted_ages == list(sorted([o.age for o in test_objs], reverse=True)))

    # next two blocsk check order by, group by, and count
    cts = tab.q.select_raw([tab['name'], doctable.f.count()], groupby=tab['name'], orderby=tab['name'].desc())
    cts_dict = [tuple(ct) for ct in cts]
    
    import collections
    cts_compare = [(k,v) for k,v in collections.Counter([o.name for o in test_objs]).items()]
    cts_compare = list(sorted(cts_compare, reverse=True))
    assert(cts_dict == cts_compare)

    exit()
    print('query title')
    for dr,title in zip(dictrows,db.select(db['title'],orderby=db['id'].asc())):
        #print(dr['title'] , title)
        assert(dr['title'] == title)
        
    print('query two')
    for dr,row in zip(dictrows,db.select([db['title'],db['age']],orderby=db['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
        
    print('query all')
    for dr,row in zip(dictrows,db.select(orderby=db['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
    
    print('query one, check num results (be sure to start with empty db)')
    assert(len(list(db.select())) == len(dictrows))
    assert(len(list(db.select(limit=1))) == 1)
    
    print('checking single aggregate function')
    sum_age = sum([dr['age'] for dr in dictrows])
    s = db.select_first(db['age'].sum())
    assert(s == sum_age)
    
    
    print('checking multiple aggregate functions')
    sum_age = sum([dr['age'] for dr in dictrows])
    sum_id = sum([i+1 for i in range(len(dictrows))])
    s = db.select_first([db['age'].sum().label('agesum'), db['id'].sum().label('idsum')])
    assert(s['agesum'] == sum_age) #NOTE: THE LABEL METHODS HERE ARENT ASSIGNED TO OUTPUT KEYS
    assert(s['idsum'] == sum_id)
    
    print('checking complicated where')
    ststr = 'user+_3'
    ct_titlematch = sum([dr['title'].startswith(ststr) for dr in dictrows])
    s = db.count(where=db['title'].like(ststr+'%'))
    assert(s == ct_titlematch)
    
    print('running conditional queries')
    minage = db.select_first(db['age'].min())
    maxid = db.select_first(db['id'].max())
    whr = (db['age'] > minage) & (db['id'] < maxid)
    s = db.select_first(db['age'].sum(), where=whr)
    sumage = sum([dr['age'] for dr in dictrows[:-1] if dr['age'] > minage])
    assert(s == sumage)
    
    print('selecting right number of elements with negation')
    maxid = db.select_first(db['id'].max())
    s = db.count(where=~(db['id'] < maxid))
    assert(s == 1)
    
    print('selecting specific rows')
    s = db.count(where=db['id'].in_([1,2]))
    assert(s == 2)
    
    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    