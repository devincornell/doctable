import os
import sys
sys.path.append('..')
import newtable
import sqlalchemy

def test_new_connectengine(test_fname: str = 'test.db'):
    if os.path.exists(test_fname):
        os.remove(test_fname) # clean for test
        
    # can't open a non-existent database using open_existing
    try:
        newtable.ConnectCore.open_existing(
            target=test_fname, 
            dialect='sqlite',
        )
        raise Exception('Should have raised FileNotFoundError.')
    except FileNotFoundError as e:
        print(e)
    
    # create a new database from scratch
    ce = newtable.ConnectCore.open_new(
        target = test_fname, 
        dialect='sqlite',
        echo = True,
    )
    

def test_sqlalchemy_table(test_table: str = 'test'):
    ce = newtable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )
    
    #print(ce)
    #return ce
    # can't reflect from a non-existent table
    try: # NOTE: database is actually created here
        tab0 = ce.reflect_sqlalchemy_table(table_name=test_table)
    except newtable.TableDoesNotExistError as e:
        print(e)
    #return ce

    # here it is added to metadata 
    tab1 = ce.sqlalchemy_table(
        table_name=test_table,
        columns=[
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('name', sqlalchemy.String),
            sqlalchemy.Column('age', sqlalchemy.Integer),
            sqlalchemy.Index('age_index', 'age'),
        ],
    ) # note that this hasn't created the database table yet
    print(tab1)
    #return ce

    # can't create a table that already exists
    try:
        tab2 = ce.sqlalchemy_table(
            table_name=test_table,
            columns=[
                sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column('name', sqlalchemy.String),
            ],
        )
        print(tab2)
        raise Exception('Should have raised TableAlreadyExistsError.')
    except newtable.TableAlreadyExistsError as e:
        print(e)

    # doesn't raise exception because extend_existing=True
    tab3 = ce.sqlalchemy_table(
        table_name=test_table,
        columns=[
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('name', sqlalchemy.String),
        ],
        extend_existing=True,
    )
    assert(tab1 is tab3)

    # essentially just gets the same table object
    tab4 = ce.reflect_sqlalchemy_table(
        table_name=test_table,
    )
    assert(tab1 is tab4)

    # should also be the same if we're just reflecting
    tab5 = ce.reflect_sqlalchemy_table(table_name=test_table)
    assert(tab1 is tab5) # they return the same reference
    
    # make sure table only created after create_all_tables
    assert(test_table not in ce.inspect_table_names())
    ce.create_all_tables()
    assert(test_table in ce.inspect_table_names())


def test_new_doctable(test_table: str = 'test'):
    ce = newtable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )

    try:
        newtable.ReflectedDocTable.from_existing_table(test_table, core=ce)
        raise Exception('Should have raised TableDoesNotExistError.')
    except newtable.TableDoesNotExistError as e:
        print(e)

    t = newtable.DocTable.from_schema(dummy_schema(), core=ce)
    print(t)

    # make sure table hasn't been created yet
    try:
        ce.inspect_columns(test_table)
        raise Exception('Should have raised NoSuchTableError.')
    except sqlalchemy.exc.NoSuchTableError as e:
        print(e)

    # create the table
    ce.create_all_tables()
    print(ce.inspect_columns(test_table))
    print(ce.inspect_indices(test_table))

    ce = newtable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )

    # now use the awesome context manager
    with ce.tables() as tables:
        t1 = tables.new_table(dummy_schema('t1'))
        t2 = tables.new_table(dummy_schema('t2'))
    print(t1, t2)
    print(ce.inspect_table_names())
    assert(len(ce.inspect_table_names()) == 2)

def test_query(test_table: str = 'test1'):
    ce = newtable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )

    with ce.tables() as tables: 
        t = tables.new_table(dummy_schema(test_table))

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
        r = tq.insert_single(TestContainer(name='a', age=110))
        assert(len(tq.select()) == 6)


import dataclasses
@dataclasses.dataclass
class TestContainer:
    id: int = None
    name: str = None
    age: int = None

    
def dummy_schema(table_name: str = 'test') -> newtable.Schema:

    return newtable.Schema(
        table_name=table_name,
        data_container = TestContainer,
        columns = {
            'id': newtable.ColumnInfo.from_type(sqlalchemy.Integer,primary_key=True),
            'name': newtable.ColumnInfo.from_type(sqlalchemy.String),
            'age': newtable.ColumnInfo.from_type(sqlalchemy.Integer),
        },
        indices = {
            f'{table_name}_age_index': newtable.IndexInfo.new('age'),
        },
        constraints = [],
        table_kwargs = {},
    )


if __name__ == '__main__':
    test_new_connectengine()
    test_sqlalchemy_table()
    test_new_doctable()
    test_query()
        
        
        