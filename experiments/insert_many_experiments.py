import sys
sys.path.append('..')
import doctable

import dataclasses
import functools
import sqlalchemy
import tempfile
import attr
import attrs
import typing



@doctable.schema
class MySchema:
    __slots__ = []
    idx: int = doctable.Col(primary_key=True, autoincrement=True)
    name: str = doctable.Col()


import collections
MySchema2NamedTuple = collections.namedtuple("MySchema2NamedTuple", ['idx', 'name'])

@attr.s(frozen=True, slots=True)
class MySchema2:
    idx: int = attrs.field(converter=int)
    name: str = attrs.field(converter=str)

    def as_named_tuple(self) -> collections.namedtuple:
        return MySchema2NamedTuple(self.idx, self.name)


if __name__ == '__main__':
    
    with tempfile.TemporaryDirectory() as td1, tempfile.TemporaryDirectory() as td2, tempfile.TemporaryDirectory() as td3:



        tab = doctable.DocTable(target=f'{td1}/tmp.db', tabname='test', schema=MySchema, new_db=True)
        oldtab = doctable.DocTable(target=f'{td1}/oldtab.db', tabname='old', schema=OldSchema, new_db=True)
        #tab2 = doctable.DocTable(target=f'{td1}/tmp.db', tabname='test', schema=MySchema, new_db=True)
        #print(tab)
    

        stepper = doctable.Stepper()


        n = 100000
        #objs_list_nt = [MySchema2(name=f'name:{i}').as_named_tuple() for i in range(n)]
        old_objs_list = [OldSchema(name=f'name:{i}') for i in range(n)]
        real_objs_list = [MySchema(name=f'name:{i}') for i in range(n)]
        objs_list = [MySchema(name=f'name:{i}')._doctable_as_dict() for i in range(n)]
        objs_dict = {i: MySchema(name=f'name:{i}')._doctable_as_dict() for i in range(n)}
        objs_gen = (MySchema(name=f'name:{i}')._doctable_as_dict() for i in range(n))
        obj = MySchema(name=f'name:hi')
        q = sqlalchemy.sql.insert(tab._table)#.values(objs_list)
        
        with tab.connect() as conn:
            
            oldtab.q.insert_single(old_objs_list[0])
            print(oldtab.head())
            obj = oldtab.q.select_first()
            print(obj)
            print(dir(obj))
            print(obj.v)
            print(obj.v.name)
            print(obj.v.a)
            
            exit()
            
            
            func = functools.partial(tab.q.insert_many, real_objs_list)
            av_time = stepper.time_call(func, num_calls=100)
            print(f'insert_many: {av_time}')
            
            
            
            print(tab.q.select_head())
            
            #av_time = stepper.time_call(functools.partial(conn.execute, q))
            #print(f'adding with .values(): {av_time}')
            
            #print(f'{type(tab.q.select_raw(limit=1)[0])=}')
            
            def test_select():
                objs = [tab.schema.row_to_object(d) for d in tab.q.select_raw()]
            av_time = stepper.time_call(test_select, num_calls=100)
            print(f'test_select: {av_time}')
            
            exit()
            
            tab.delete()
            
            q = sqlalchemy.sql.insert(tab._table).values(objs_list)
            av_time = stepper.time_call(functools.partial(conn.execute, q))
            print(f'adding with .values(): {av_time}')

            q = sqlalchemy.sql.insert(tab._table).values(objs_list[0])
            av_time = stepper.time_call(functools.partial(conn.execute, q))
            print(f'adding with .values(): {av_time}')

            tab.delete()

            q = sqlalchemy.sql.insert(tab._table)
            av_time = stepper.time_call(functools.partial(conn.execute, q, objs_list))
            print(f'adding with .execute(): {av_time}')

            q = sqlalchemy.sql.insert(tab._table)
            av_time = stepper.time_call(functools.partial(conn.execute, q, objs_list[0]))
            print(f'adding with .execute(): {av_time}')

            tab.delete()

            q = sqlalchemy.sql.insert(tab._table, objs_list)
            av_time = stepper.time_call(functools.partial(conn.execute, q))
            print(f'adding with .insert(): {av_time}')
        
            q = sqlalchemy.sql.insert(tab._table, objs_list[0])
            av_time = stepper.time_call(functools.partial(conn.execute, q))
            print(f'adding with .insert(): {av_time}')

        #print(q.execute())
        #tab._execute(q)

        print(tab.head())
