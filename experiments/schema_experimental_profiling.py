import sys
sys.path.append('..')
import doctable
import dataclasses
import functools
import tempfile
import random
import copy
import typing
import cProfile

@doctable.schema
class MyObjSmall:
    __slots__ = []
    id: int = doctable.Col()
    name: str = doctable.Col()
    other: float = doctable.Col()
    other2: float = doctable.Col()

@doctable.schema_experimental
class ExMyObjSmall:
    id: int = doctable.ExpIDCol()
    name: str = doctable.ExpCol()
    other: float = doctable.Col()
    other2: float = doctable.Col()

def make_test_dt(SchemaClass, in_memory: bool = True, tmpdir: str = None) -> doctable.DocTable:
    dt_small = doctable.DocTable(
        schema=SchemaClass,
        target = ':memory:' if in_memory else f'{tmpdir}/{SchemaClass}_test.db',
        new_db = True,
    )
    return dt_small

def test_insert_and_select(test_objs: typing.List[MyObjSmall], table: doctable.DocTable):
    with table as tab:
        tab.q.insert_multi(test_objs)
        a = tab.q.select()

def runtest_exp(n: int = 100):
    print(f'=== start EXPERIMENTAL test: {n=} ================')
    with tempfile.TemporaryDirectory() as tmpdir:
        dt_small = make_test_dt(ExMyObjSmall, tmpdir)
        print(f'construct {n} objects')
        [ExMyObjSmall(i, f'name_{i}') for i in range(n)]
        #[ExMyObjSmall.from_dict({'id': i, 'name': f'name_{i}'}) for i in range(n)]
        test_objs = [ExMyObjSmall(i, f'name_{i}') for i in range(n)]

def runtest_obj(n: int = 100):
    print(f'=== start OBJECT test: {n=} ================')
    with tempfile.TemporaryDirectory() as tmpdir:
        dt_small = make_test_dt(MyObjSmall, tmpdir)
        print(f'construct {n} objects')
        test_objs = [MyObjSmall(i, f'name_{i}') for i in range(n)]

def runtest_raw(n: int = 100):
    print(f'=== start RAW test: {n=} ================')
    with tempfile.TemporaryDirectory() as tmpdir:
        dt_small = make_test_dt(MyObjSmall, tmpdir)
        print(f'construct {n} objects')
        test_objs = [{'id': i, 'name': f'name_{i}'} for i in range(n)]

def test_create_objects(ObjType: type, payload: typing.List[typing.Tuple[int,str]]):
    for p in payload:
        ObjType(**p)

def test_create_objects_raw(construct_func: typing.Callable, payload: typing.List[typing.Tuple[int,str]]):
    for p in payload:
        construct_func(_doctable_rowdict=p)

# these can't be in __main__
n = 500000
payload = [(i, f'name{i}', i * 1.1, i * 2.1) for i in range(n)]
payload_raw = [{'id': i, 'name': f'name{i}', 'other': i * 1.1, 'other2': i * 2.1} for i in range(n)]

cProfile.run('test_create_objects(MyObjSmall, payload_raw)', filename='bench/schema_obj_create.prof')
cProfile.run('test_create_objects(ExMyObjSmall, payload_raw)', filename='bench/schema_experimental_obj_create.prof')
cProfile.run('test_create_objects_raw(ExMyObjSmall, payload_raw)', filename='bench/schema_experimental_raw_obj_create.prof')

if __name__ == '__main__':
    
    pass


