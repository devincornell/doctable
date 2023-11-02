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

@doctable.schema_experimental
class ExpObj:
    id: int = doctable.ExpIDCol()
    name: int = doctable.ExpCol()
    extra: typing.Any = doctable.ExpCol()
    extra2: int = doctable.ExpCol()

    
def test_properties_schema(num_rows: int = 10):
    #print(id(doctable.MISSING_VALUE))
    tmpf = tempfile.TemporaryDirectory('mytmp')

    #o = ExpObj(name=f'Devin')
    # note: this intentionally weird - we'll ignore any result that isn't a class attr
    rowdata = {'name': 'devin', 'whateva': 123}
    o = ExpObj._doctable_from_row_obj(rowdata)

    print(o) # sweet this looks fine
    assert(o.name == rowdata['name'])
    try:
        print(o.whateva)
    except AttributeError:
        print(f'caught exception sucecssfully')

    try:
        o = ExpObj(name = 'Devin', however='ha')
    except TypeError:
        print('caught exception normally')
    
    o = ExpObj(name = 'Devin', extra=5)
    print(o.name)
    print(o)

    tab = doctable.DocTable(target=':memory:', schema=ExpObj)
    tab.q.insert_single(ExpObj(name='Devin'))
    print(tab.q.select_first())


    return 

    ############################### Old Schema Method #########################
    oldobjs = [ExpObj(name=f'User {i}') for i in range(num_rows)]
    print(type(oldobjs[0]))
    print('extra:', oldobjs[0].extra)
    print(oldobjs[0].id)

    assert(oldobjs[0].id is doctable.MISSING_VALUE)
    assert(oldobjs[0].name == 'User 0')
    assert(oldobjs[0].extra is doctable.MISSING_VALUE)
    assert(oldobjs[0].extra2 == 0)
    
    tab = get_newtab(tmpf, ExpObj)
    tab.insert(oldobjs)
    print(tab.count())

    db_oldobjs = tab.select()
    assert(len(db_oldobjs) == len(oldobjs))
    assert(db_oldobjs[0].id is not doctable.MISSING_VALUE)
    assert(db_oldobjs[0].name == 'User 0')
    assert(db_oldobjs[0].extra is None)
    assert(db_oldobjs[0].extra2 == 0)

    db_oldobjs = tab.q.select(['name'])
    assert(len(db_oldobjs) == len(oldobjs))
    assert(db_oldobjs[0].id is doctable.MISSING_VALUE)
    assert(db_oldobjs[0].name == 'User 0')
    assert(db_oldobjs[0].extra is doctable.MISSING_VALUE)
    assert(db_oldobjs[0].extra2 == 0)

    ############################### New Schema Method #########################

    newobjs = [ExpObj(name=f'User {i}') for i in range(num_rows)]
    
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

def test_slots():
    # make sure it is a slots class
    pass

if __name__ == '__main__':
    test_properties_schema()
    test_slots()



