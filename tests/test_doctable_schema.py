

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
    id: int = doctable.Col()
    name: int = doctable.Col()
    extra: typing.Any = doctable.Col()
    extra2: int = 0
    
@doctable.schema
class NewObj:
    __slots__ = []
    id: int = doctable.Col()
    name: int = doctable.Col()
    extra: typing.Any = doctable.Col()
    extra2: int = 0
    
def test_properties_schema(num_rows: int = 10):
    #print(id(doctable.MISSING_VALUE))
    tmpf = tempfile.TemporaryDirectory('mytmp')
    
    oldobjs = [OldObj(id=i, name=f'User {i}') for i in range(num_rows)]
    print('extra:', oldobjs[0].extra)
    assert(oldobjs[0].extra is doctable.MISSING_VALUE)
    
    tab = get_newtab(tmpf, OldObj)
    print(tab)
    
    tab.insert(oldobjs)
    print(tab.count())
    
    db_oldobjs = tab.select(['name'])
    assert(len(db_oldobjs) == len(oldobjs))
    print('id:', db_oldobjs[0].id)
    print(db_oldobjs[0])
    assert(db_oldobjs[0].id is doctable.MISSING_VALUE)

    newobjs = [NewObj(id=i, name=f'User {i}') for i in range(num_rows)]
    tab = get_newtab(tmpf, NewObj)
    print(tab)
    tab.insert(newobjs)
    db_newobjs = tab.select(['name'])
    print(db_newobjs[0].name)
    
    # compare differences in underlying schemas
    print(dir(db_oldobjs[0]))
    print(dir(db_newobjs[0]))
    
    
    with pytest.raises(doctable.ValueNotRetrievedEror) as e:
        print(db_newobjs[0].id)

def test_slots():
    # make sure it is a slots class
    newobj = NewObj()
    depricobj = OldObj()
    
    assert(not hasattr(newobj, '__dict__'))
    assert(not hasattr(depricobj, '__dict__'))
    assert(len(newobj._doctable_as_dict()) == 0) # ignores MISSING_VALUE
    assert(len(depricobj._doctable_as_dict()) == 0) # ignores MISSING_VALUE

if __name__ == '__main__':
    test_properties_schema()
    test_slots()



