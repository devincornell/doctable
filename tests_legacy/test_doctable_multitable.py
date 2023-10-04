
import pytest
import sqlalchemy
#from doctable.schemas import parse_schema

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable
#from doctable.schemas import parse_schema
    
    
    
class Parent(doctable.DocTable):
    _tabname_ = 'parent'
    _schema_ = (
        ('idcol', 'id'),
        ('string', 'name', dict(unique=True)),
        ('integer', 'age', dict(default=10))
    )
    
class Child(doctable.DocTable):
    _tabname_ = 'child'
    _schema_ = (
        ('idcol', 'id'),
        ('integer', 'name'),
        
        ('string', 'par'),
        ('foreignkey', 'par', 'parent.name', dict(onupdate="CASCADE", ondelete="CASCADE")),
    )
    
def test_foreignkeys():
    eng = doctable.ConnectEngine(target=':memory:', echo=False, foreign_keys=True)
    pdb = Parent(engine=eng)
    cdb = Child(engine=eng)
    print(cdb.list_tables())
    
    
    pdb.insert([
        {'name': 'eric dumb'},
        {'name': 'carnivore'},
    ])
    
    cdb.insert({'name':'cal', 'par':'eric dumb'})
    cdb.insert({'name':'dorukus', 'par':'carnivore'})
    cdb.insert({'name':'salinas', 'par':'carnivore'})
    
    p_count, c_count = pdb.count(), cdb.count()
    
    
    # can't insert new element that does not have parent
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        cdb.insert({'name':'joseph', 'par':'randomname'})
    
    
    print(pdb.select_df())
    print(cdb.select_df())
    
    pdb.delete(wherestr='name=="carnivore"')
    
    print('---')
    print(pdb.select_df())
    print(cdb.select_df())
    
    # make sure delete cascade worked
    assert(cdb.count() == c_count-2)
    

if __name__ == '__main__':
    test_foreignkeys()
