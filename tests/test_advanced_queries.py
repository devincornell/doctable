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
import tempfile

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
    
def test_advanced_queries():
    with tempfile.TemporaryDirectory() as tmp:

        eng = doctable.ConnectEngine(target=f'{tmp}/tmp_984237.db', new_db=True)
        assert(len(eng.list_tables())==0)
        print(eng)

        cdb = ChildTable(engine=eng)
        pdb = ParentTable(engine=eng)
        

        print(pdb, cdb)
        assert(len(eng.list_tables())==2)

        pdb.q.insert_single(Parent(name='whateva'))
        
        childs = [Child(name=f'Bo {i}', parent_name='whateva') for i in range(10)]
        childs += [Child(name=f'Bo {i}', parent_name='dos') for i in range(11)]
        cdb.q.insert_multi(childs)
        
        print(cdb.columns)
        df = cdb.q.select_df([cdb['parent_name'], doctable.f.count()], groupby=cdb['parent_name'], verbose=True)
        print(df)
        assert(df.shape[0] == 2)
        cts = cdb.q.select_raw([cdb['parent_name'], doctable.f.count()], groupby=cdb['parent_name'], verbose=True)
        print(cts)
        assert(len(cts) == 2)
        assert(len(cts[0]) == 2)

        f = doctable.f
        cols = [cdb['parent_name'], f.count().label('ct')]
        cts = cdb.q.select_raw(cols, groupby=cdb['parent_name'], orderby=f.asc('ct'))
        assert(cts[0]['ct'] < cts[1]['ct'])

if __name__ == '__main__':
    test_advanced_queries()


