

import pytest
import sqlalchemy
import tempfile
import random
import typing


import sys
sys.path.append('..')
import doctable

def get_newtab(tempfolder: tempfile.TemporaryDirectory, SchemaObj: type):
    target = f'{tempfolder.name}/{random.randrange(9999)}.db'
    tab = doctable.DocTable(target=target, schema=SchemaObj, new_db=True)
    tab.delete()
    assert(tab.count() == 0)
    return tab




@doctable.schema_depric
class OldObj:
    __slots__ = []
    id: int = doctable.IDCol()
    name: int = doctable.Col()
    extra: typing.Any = doctable.Col()
    extra2: int = 0
    
@doctable.schema
class NewObj:
    __slots__ = []
    id: int = doctable.IDCol()
    name: int = doctable.Col()
    extra: typing.Any = doctable.Col()
    extra2: int = 0
    
def test_properties_schema(num_rows: int = 10):
    #print(id(doctable.MISSING_VALUE))
    tmpf = tempfile.TemporaryDirectory('mytmp')
    
    ############################### Old Schema Method #########################
    oldobjs = [OldObj(name=f'User {i}') for i in range(num_rows)]
    print('extra:', oldobjs[0].extra)
    
    assert(oldobjs[0].id is doctable.MISSING_VALUE)
    assert(oldobjs[0].name == 'User 0')
    assert(oldobjs[0].extra is doctable.MISSING_VALUE)
    assert(oldobjs[0].extra2 == 0)
    
    tab = get_newtab(tmpf, OldObj)
    tab.insert(oldobjs)
    print(tab.count())

    db_oldobjs = tab.select()
    assert(len(db_oldobjs) == len(oldobjs))
    assert(db_oldobjs[0].id is not doctable.MISSING_VALUE)
    assert(db_oldobjs[0].name == 'User 0')
    assert(db_oldobjs[0].extra is None)
    assert(db_oldobjs[0].extra2 == 0)

    db_oldobjs = tab.select(['name'])
    assert(len(db_oldobjs) == len(oldobjs))
    assert(db_oldobjs[0].id is doctable.MISSING_VALUE)
    assert(db_oldobjs[0].name == 'User 0')
    assert(db_oldobjs[0].extra is doctable.MISSING_VALUE)
    assert(db_oldobjs[0].extra2 is doctable.MISSING_VALUE)

    ############################### New Schema Method #########################

    newobjs = [NewObj(name=f'User {i}') for i in range(num_rows)]
    
    with pytest.raises(doctable.DataNotAvailableError) as e:
        newobjs[0].id
    assert(newobjs[0].name == 'User 0')
    with pytest.raises(doctable.DataNotAvailableError) as e:
        newobjs[0].extra
    assert(newobjs[0].extra2 == 0)
    
    tab = get_newtab(tmpf, NewObj)
    tab.insert(newobjs)
    print(tab.count())

    db_newobjs = tab.select()
    assert(len(db_newobjs) == len(oldobjs))
    assert(db_newobjs[0].id is not doctable.MISSING_VALUE)
    assert(db_newobjs[0].name == 'User 0')
    assert(db_newobjs[0].extra is None)
    assert(db_newobjs[0].extra2 == 0)

    db_newobjs = tab.select(['name'])
    assert(len(db_newobjs) == len(oldobjs))
    with pytest.raises(doctable.DataNotAvailableError) as e:
        db_newobjs[0].id
    assert(db_newobjs[0].name == 'User 0')
    with pytest.raises(doctable.DataNotAvailableError) as e:
        db_newobjs[0].extra
    with pytest.raises(doctable.DataNotAvailableError) as e:
        db_newobjs[0].extra2
    

def test_slots():
    # make sure it is a slots class
    newobj = NewObj()
    oldobj = OldObj()
    
    assert(not hasattr(newobj, '__dict__'))
    assert(not hasattr(oldobj, '__dict__'))
    assert(len(newobj._doctable_as_dict()) == 1) # ignores MISSING_VALUE
    assert(len(oldobj._doctable_as_dict()) == 1) # ignores MISSING_VALUE

    with pytest.raises(doctable.SlotsRequiredError) as e:
        @doctable.schema
        class TestSchema:
            idx: int

if __name__ == '__main__':
    test_properties_schema()
    test_slots()



