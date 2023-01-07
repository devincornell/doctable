import sys
sys.path.append('..')
import doctable

import functools
import sqlalchemy
import tempfile
import attr
import attrs




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
        #tab2 = doctable.DocTable(target=f'{td1}/tmp.db', tabname='test', schema=MySchema, new_db=True)
        #print(tab)
        

        stepper = doctable.Stepper()


        n = 100000
        #objs_list_nt = [MySchema2(name=f'name:{i}').as_named_tuple() for i in range(n)]
        objs_list = [MySchema(name=f'name:{i}')._doctable_as_dict() for i in range(n)]
        objs_dict = {i: MySchema(name=f'name:{i}')._doctable_as_dict() for i in range(n)}
        objs_gen = (MySchema(name=f'name:{i}')._doctable_as_dict() for i in range(n))
        obj = MySchema(name=f'name:hi')
        q = sqlalchemy.sql.insert(tab._table)#.values(objs_list)
        
        with tab.connect() as conn:

            #tab.execute, q, objs_list[0]
            q = sqlalchemy.sql.insert(tab._table)
            newobj = MySchema2(0, 'hi')
            nt = attr.asdict(newobj)
            print(nt)
            conn.execute(q, {MySchema(name='hi'), MySchema(name='hello')})
            exit()
            


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
