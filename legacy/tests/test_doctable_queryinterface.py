import random
from time import time
import datetime
import functools

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
    test_dicts = [o.asdict_ignore_missing() for o in test_objs]
    
    m = MyObj(name='joe')
    assert(m.v['id'] is doctable.MISSING_VALUE)
    assert(m.v['age'] is doctable.MISSING_VALUE)
    assert(m.v['added'] is doctable.MISSING_VALUE)
    assert(m.v['updated'] is doctable.MISSING_VALUE)
    assert(m.v['name'] is not doctable.MISSING_VALUE)
    
    with pytest.raises(doctable.RowDataNotAvailableError):
        m.id
    with pytest.raises(doctable.RowDataNotAvailableError):
        m.age
    with pytest.raises(doctable.RowDataNotAvailableError):
        m.added
    with pytest.raises(doctable.RowDataNotAvailableError):
        m.updated
        
    #with pytest.raises(doctable.ObjectToDictCovnersionFailedError):
    #    tab.q.insert_single(o.asdict_ignore_missing())

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
            tab.q.insert_single(o.asdict_ignore_missing())

        tab.q.insert_single_raw(o.asdict_ignore_missing())
        
        with pytest.raises(doctable.sqlalchemy.exc.ArgumentError):
            tab.q.insert_single_raw(o)

        with pytest.raises(TypeError):
            tab.q.insert_multi(o)
            tab.q.insert_multi_raw(o)
            tab.q.insert_multi(o.asdict_ignore_missing())
            tab.q.insert_multi_raw(o.asdict_ignore_missing())

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

    stepper = doctable.Stepper()
    
    
    
    @doctable.schema(enable_properties=False)
    class MyOldObj:
        __slots__ = []
        id: int = doctable.IDCol()
        name: str = doctable.Col()
        age: int = doctable.Col()
        added: datetime.datetime = doctable.AddedCol()
        updated: datetime.datetime = doctable.UpdatedCol()

    oldtab = doctable.DocTable(target=':memory:', schema=MyOldObj)
    old_test_objs = [MyOldObj(name=f'User{i//2}', age=i) for i in range(100)]
    new_test_objs = [MyObj(name=f'User{i//2}', age=i) for i in range(100)]
    
    stepper.step(f'running second test with {len(old_test_objs)} objects.')
    #print(stepper.time_call(functools.partial(tab.q.insert_multi, old_test_objs), as_str=True, num_calls=2))




    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    