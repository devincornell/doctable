
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
    
def test_engine_basics():
    eng = doctable.ConnectEngine(':memory:', echo=True)
    print(eng)
    pdb = Parent(engine=eng)
    cdb = Child(engine=eng)
    print(pdb)
    

if __name__ == '__main__':
    test_engine_basics()
