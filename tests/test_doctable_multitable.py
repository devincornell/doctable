
import pytest
import sqlalchemy
#from doctable.schemas import parse_schema

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable
#from doctable.schemas import parse_schema
    
@doctable.schema
class Parent:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col(unique=True)
    age: int = doctable.Col(default=10)
    
    
class ParentTable(doctable.DocTable):
    _tabname_ = 'parent'
    _schema_ = Parent
    
@doctable.schema
class Child:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    parent_name: str = doctable.Col()

class ChildTable(doctable.DocTable):
    _tabname_ = 'child'
    _schema_ = Child
    _constraints_ = [
        doctable.Constraint('foreignkey', ['parent_name'], ['parent.name'], onupdate="CASCADE", ondelete="CASCADE"),
    ]
    
def test_foreignkeys():
    tempfolder = doctable.TempFolder('tmp')
    eng = doctable.ConnectEngine(target='tmp/rando.db', new_db=True, foreign_keys=True)
    pdb = ParentTable(engine=eng)
    cdb = ChildTable(engine=eng)
    print(cdb.list_tables())
    
    
    pdb.insert([
        {'name': 'eric dumb'},
        {'name': 'carnivore'},
    ])
    
    cdb.insert({'name':'cal', 'parent_name':'eric dumb'})
    cdb.insert({'name':'dorukus', 'parent_name':'carnivore'})
    cdb.insert({'name':'salinas', 'parent_name':'carnivore'})
    child_count = cdb.count()
    parent_count = pdb.count()
    print(f'{pdb.select_df()}\n=======\n{cdb.select_df()}\n============')

    # can't insert new element that does not have parent
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        cdb.insert({'name':'joseph', 'parent_name':'aklhsjfkjhs'})
    
    # make sure delete cascade worked
    pdb.delete(wherestr='name=="carnivore"')
    assert(cdb.count() == child_count-2)
    

if __name__ == '__main__':
    test_foreignkeys()
