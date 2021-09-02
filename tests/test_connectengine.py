import gc
import pytest
import sqlalchemy
#from doctable.schemas import parse_schema
import time
import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable
#from doctable.schemas import parse_schema
import pickle
    

@doctable.schema
class Parent:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()

class ParentTable(doctable.DocTable):
    _tabname_ = 'parents'
    _schema_ = Parent
    def get_children_table(self, **kwargs):
        return ChildTable(engine=self.engine, **kwargs)
    
@doctable.schema
class Child:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    parent_name: str = doctable.Col()

class ChildTable(doctable.DocTable):
    _tabname_ = 'children'
    _schema_ = Child
    _constraints_ = (
        doctable.Constraint('foreignkey', ('parent_name',), ('parents.name',)),
    )
    
def processfunc(nums, eng):
    eng.reopen()
    print(eng)
    pdb = Parent(engine=eng)
    cdb = ChildTable(engine=eng)
    print(pdb, cdb)
    
def test_engine_basics():
    with doctable.TempFolder('tmp') as tmp:
        
        eng = doctable.ConnectEngine(target='tmp/tmp_984237.db', new_db=True)
        assert(len(eng.list_tables())==0)
        print(eng)

        pdb = ParentTable(engine=eng)
        cdb = pdb.get_children_table()
        print(pdb, cdb)
        assert(len(eng.list_tables())==2)

        pdb.insert(Parent(name='whateva'))
        cdb.insert(Child(name='whateva child', parent_name='whateva'))
        
        #with doctable.Distribute(2) as d:
        #    d.map_chunk(processfunc, [1,2], eng)


if __name__ == '__main__':
    test_engine_basics()


