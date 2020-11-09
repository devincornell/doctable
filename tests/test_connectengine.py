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
    
    
class Parent(doctable.DocTable):
    __tabname__ = 'parent'
    __args__ = {
        'engine_kwargs':{
            'foreign_keys':True,
            #'timeout': 30,
        },
    }
    __schema__ = (
        ('idcol', 'id'),
        ('string', 'name', dict(unique=True)),
        ('integer', 'age', dict(default=10))
    )
    def get_childdb(self, **kwargs):
        return Child(engine=self.engine, **kwargs)
    
class Child(doctable.DocTable):
    __tabname__ = 'child'
    __schema__ = (
        ('idcol', 'id'),
        ('string', 'name'),
        ('string', 'parent_name'), 
        ('foreignkey', 'parent_name', 'parent.name'), 
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
    cdb = pdb.get_childdb()
    pdb2 = Parent(target='tmp.db')
    #print(pdb)
    pdb.insert({'name':'whateva'}, ifnotunique='replace')
    print(cdb)
    print(pdb)
    print(pdb2)
    
    with doctable.Distribute(2) as d:
        d.map_chunk(processfunc, [1,2], eng)


def test_engine_connections():
    tmp_fname = 'tmp.db'
    eng = doctable.ConnectEngine(tmp_fname, new_db=True)
    print(eng)
    pdb = Parent(engine=eng, verbose=True)
    cdb = pdb.get_childdb(verbose=True)
    #pdb2 = Parent(target=tmp_fname)
    
    #print(dir(eng._engine.pool))
    #print(eng._engine.pool.unique_connection().close())
    pdb.insert({'name':'whateva'}, ifnotunique='replace')
    cdb.insert({'name': 'cal', 'parent_name':'whateva'})
    print(cdb._conn)
    print(pdb._conn)
    #print(pdb2._conn)

    eng.dispose()
    print(cdb.select_first())
    cdb.insert({'name':'carlos', 'parent_name': 'whateva'})
    
    #time.sleep(1)
    allrows = list()
    for row in pdb.select(where=pdb['name']==cdb['parent_name']):
        allrows.append(row)
        print(row)
    #cdb.close_conn()
    print(f'{len(allrows)}: {allrows[0]}')

    def write_pic(data, fname):
        with open(fname, 'wb') as f:
            pickle.dump(data, f)

    write_pic(allrows, 'tmp.pic')
    

if __name__ == '__main__':
    #test_engine_basics()
    #test_engine_connections()

    tmp_fname = 'tmp.db'
    eng = doctable.ConnectEngine(tmp_fname, new_db=True)
    print(eng)
    pdb = Parent(engine=eng, verbose=True)
    cdb = pdb.get_childdb(verbose=True)
    #pdb2 = Parent(target=tmp_fname)
    
    #print(dir(eng._engine.pool))
    #print(eng._engine.pool.unique_connection().close())
    pdb.insert({'name':'whateva'}, ifnotunique='replace')
    cdb.insert({'name': 'cal', 'parent_name':'whateva'})
    print(cdb._conn)
    print(pdb._conn)
    #print(pdb2._conn)

    eng.dispose()
    print(cdb.select_first())
    cdb.insert({'name':'carlos', 'parent_name': 'whateva'})
    
    #time.sleep(1)
    allrows = list()
    for row in pdb.select(where=pdb['name']==cdb['parent_name']):
        allrows.append(row)
        print(row)
    #cdb.close_conn()
    print(f'{len(allrows)}: {allrows[0]}')

    def write_pic(data, fname):
        with open(fname, 'wb') as f:
            pickle.dump(data, f)
    #del pdb._engine
    #del cdb._engine
    #del eng
    #del pdb
    #del cdb
    write_pic(allrows, 'tmp.pic')
