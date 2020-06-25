
import pytest
import sqlalchemy
#from doctable.schemas import parse_schema

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable
#from doctable.schemas import parse_schema
    
    
    
class Parent(doctable.DocTable):
    __tabname__ = 'parent'
    __schema__ = (
        ('idcol', 'id'),
        ('string', 'name', dict(unique=True)),
        ('integer', 'age', dict(default=10))
    )
    
class Child(doctable.DocTable):
    __tabname__ = 'child'
    __schema__ = (
        ('idcol', 'id'),
        ('integer', 'name'),
        ('string', 'par'),
    )
    
def processfunc(nums, eng):
    eng.reopen()
    print(eng)
    pdb = Parent(engine=eng)
    print(pdb)
    
def test_engine_basics():
    eng = doctable.ConnectEngine('tmp.db', new_db=True)
    print(eng)
    pdb = Parent(engine=eng)
    cdb = Child(engine=eng)
    pdb2 = Parent(target='tmp.db')
    #print(pdb)
    pdb.insert({'name':'whateva'}, ifnotunique='replace')
    print(cdb)
    print(pdb)
    print(pdb2)
    
    with doctable.Distribute(2) as d:
        d.map_chunk(processfunc, [1,2], eng)
    

if __name__ == '__main__':
    test_engine_basics()
