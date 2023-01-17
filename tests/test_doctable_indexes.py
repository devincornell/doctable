import random
from time import time
import datetime
import functools

import sys
sys.path.append('..')
import typing
import doctable
import sqlalchemy
import pytest

@doctable.schema
class MyObj1:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col(index=True)
    added: datetime.datetime = doctable.AddedCol()

@doctable.schema
class MyObj2:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    #age: int = doctable.Col()
    added: datetime.datetime = doctable.AddedCol()
    _indices_ = [
        doctable.Index('ind_added', 'added'),
        doctable.Index('ind_name_added', 'name', 'added', unique=True),
    ]
    
@doctable.schema
class MyObj3:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    added: datetime.datetime = doctable.AddedCol()
    _indices_ = [
        doctable.Index('ind_added', 'added'),
        doctable.Index('ind_name_added', 'name', 'added', unique=True),
    ]
    
@doctable.schema
class MyObj4:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    added: datetime.datetime = doctable.AddedCol()
    _indices_ = [
        doctable.Index('ind_whatchama', 'whatchama'),
        doctable.Index('ind_name_added', 'name', 'added', unique=True),
    ]

    
def test_select_iter_basic():
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmp:
        fname = f'{tmp}/testdb.db'
        
        if False:
            ce = doctable.ConnectEngine(target=fname, new_db=True)
            schema = doctable.DataclassSchema.from_schema_definition(MyObj2)
            table = ce.new_table('mytab', schema.columns)
            table.create(ce._engine)
            #ind = schema.indices[0]
            #print(ind)
            ind = sqlalchemy.Index('myname', table.c.name)
            print(ind)
            ind.create(bind=ce._engine)
            exit()
        
        print(f'============================== tab =================================')
        tab = doctable.DocTable(target=fname, schema=MyObj1, tabname='mytab_old', new_db=True)
        #print(tab.schema.columns)
        #print(tab.schema_table())
        print(f'{tab.indices()=}')
        
        print(f'============================== tab1 =================================')
        tab1 = doctable.DocTable(target=fname, schema=MyObj1, tabname='mytab')
        #print(tab1.schema.columns)
        #print(tab1.schema_table())
        print(f'{tab1.indices()=}')
        
        print(f'============================== tab2 =================================')
        tab2 = doctable.DocTable(target=fname, schema=MyObj2, tabname='mytab', allow_inconsistent_schema=False)
        #tab2 = doctable.DocTable(target=fname, schema=MyObj2, tabname='mytab')
        #print(tab2.schema.columns)
        #print(tab2.schema_table())
        print(f'{tab2.indices()=}')
        
        print(f'============================== tab3 =================================')
        tab3 = doctable.DocTable(engine=tab1.engine, schema=MyObj2, tabname='mytab', allow_inconsistent_schema=True)
        #print(tab3.schema.columns)
        #print(tab3.schema_table())
        print(f'{tab3.indices()=}')
        
        print(f'============================== tab4 =================================')
        tab4 = doctable.DocTable(target=fname, tabname='mytab')
        #print(tab3.schema.columns)
        #print(tab4.schema_table())
        print(f'{tab4.indices()=}')
        
        print(f'============================== later stuff =================================')
        print(tab.engine.inspector.get_indexes('mytab'))
        t = tab2.engine.tables['mytab']
        print(t.columns)
        
        


if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    