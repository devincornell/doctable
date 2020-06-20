
import pytest
import sqlalchemy
#from doctable.schemas import parse_schema

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable
#from doctable.schemas import parse_schema
    
    
    
class Parent(doctable.DocTable):
    tabname = 'parent'
    schema = (
        ('idcol', 'id'),
        ('string', 'name', dict(unique=True)),
        ('integer', 'age', dict(default=10))
    )
    
class Child(doctable.DocTable):
    tabname = 'child'
    schema = (
        ('idcol', 'id'),
        ('integer', 'name'),
        ('string', 'par'),
    )
    
def test_thread(nums, eng):
    eng.reopen()
    print(eng)
    pdb = Parent(engine=eng)
    print(pdb)
    
def test_engine_basics():
    eng = doctable.ConnectEngine(':memory:', echo=False)
    print(eng)
    pdb = Parent(engine=eng)
    cdb = Child(engine=eng)
    pdb2 = Parent(engine=eng)
    #print(pdb)
    pdb.insert({'name':'whateva'})
    print(pdb)
    print(pdb2)
    
    with doctable.Distribute(2) as d:
        d.map_chunk(test_thread, [1,2], eng)
    

if __name__ == '__main__':
    test_engine_basics()
