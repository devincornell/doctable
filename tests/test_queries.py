import datetime
import os
import sqlalchemy

import sys
sys.path.append('..')
import doctable



def dummy_container1(table_name: str = 'test') -> doctable.Container:
    @doctable.table_schema(table_name=table_name)
    class DummyContainer:
        name: str
        age: int
        id: int = doctable.Column(column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True))

    return DummyContainer


def test_query(test_table: str = 'test1'):
    ce = doctable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )

    Container = dummy_container1(test_table)
    with ce.begin_ddl() as emitter: 
        t = emitter.create_table(Container)

    # alternatively, do the same thing with query()
    with ce.query() as q:
        r = q.execute_string(
            f"INSERT INTO {test_table} (name, age) VALUES (:name, :age)",
            [{"name": 'a', "age": 1}, {"name": 'b', "age": 4}],
        )
        print(r)
        r = q.select(t.all_cols()).all()
        print(r)
        assert(len(r) == 2)

        r = q.select(t.all_cols(), where=t['age'] > 2).all()
        assert(len(r) == 1)

        q.insert_multi(t, data=[
            {'name': 'a', 'age': 1},
            {'name': 'a', 'age': 10},
        ])
        r = q.select(t.all_cols(), where=t['age'] > 2).all()
        assert(len(r) == 2)
        r = q.select(t.cols('name'), where=t['age'] > 2, limit=10).all()
        assert(len(r) == 2)

        q.insert_single(t, data={'name': 'a', 'age': 100})
        r = q.select(t.cols('name'), where=t['age'] > 2, limit=10).all()
        assert(len(r) == 3)

        q.update_single(t, where=t['age'] > 50, values={'name': 'oldy'})
        r = q.select(t.all_cols(), where=t['name'] == 'oldy').all()
        assert(len(r) == 1)

    with t.query() as tq:
        assert(len(tq.select()) == 5)
        r = tq.insert_single(Container(name='a', age=110))
        assert(len(tq.select()) == 6)



if __name__ == '__main__':
    test_query()
    