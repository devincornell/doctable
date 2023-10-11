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
    with ce.tablemaker() as tmaker:
        t1 = tmaker.new_table(dummy_schema('t1'))
        t2 = tmaker.new_table(dummy_schema('t2'))
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
        r = tq.insert_single(TestDataClass(name='a', age=110))
        assert(len(tq.select()) == 6)


import dataclasses
@dataclasses.dataclass
class TestDataClass:
    id: int = None
    name: str = None
    age: int = None


def dummy_container(table_name: str = 'test') -> newtable.Container:
    @newtable.table_schema()
    class TestContainer:
        id: int = newtable.IDColumn()
        name: str
        age: int

    return TestContainer



def dummy_schema(table_name: str = 'test') -> newtable.TableSchema:
    return newtable.TableSchema(
        table_name=table_name,
        container_type = TestDataClass,
        columns = [
            newtable.ColumnInfo.default('id', int),
            newtable.ColumnInfo.default('name', str),
            newtable.ColumnInfo.default('age', int),
        ],
        indices = [
            newtable.IndexInfo.default('age_index', 'age'),
        ],
        constraints = [],
        table_kwargs = {},
    )

def test_schema_definitions():

    @newtable.table_schema
    class TestContainer0:
        id: int = None
        name: str = None
        age: int = None

    assert(dataclasses.is_dataclass(TestContainer0))
    assert(newtable.SCHEMA_ATTRIBUTE_NAME in dir(TestContainer0))
    schema = getattr(TestContainer0, newtable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'TestContainer0')

    # test the most basic usage
    @newtable.table_schema()
    class TestContainer1:
        id: int
        name: str
        age: int

    assert(dataclasses.is_dataclass(TestContainer1))
    assert(newtable.SCHEMA_ATTRIBUTE_NAME in dir(TestContainer1))
    schema = getattr(TestContainer1, newtable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'TestContainer1')

    # make sure the arguments work with it
    if sys.version_info.minor >= 10:
        newtable.table_schema(TestDataClass, slots=True)
    else:
        try:
            newtable.table_schema(TestDataClass, slots=True)
            raise Exception('Should have raised TypeError.')
        except TypeError as e:
            print(e)

    @newtable.table_schema(
        indices = {
            'age_index': newtable.Index('age'),
        },
    )
    class TestContainer2:
        id: int = newtable.IDColumn()
        name: str
        age: int
    
    assert(dataclasses.is_dataclass(TestContainer2))
    assert(newtable.SCHEMA_ATTRIBUTE_NAME in dir(TestContainer2))
    schema = getattr(TestContainer2, newtable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'TestContainer2')
    
    @newtable.table_schema(
        table_name='mytable',
    )
    class TestContainer3:
        id: int = newtable.IDColumn()
        name: str
        age: int
    
    schema = getattr(TestContainer3, newtable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'mytable')

    tc = TestContainer3(id=1, name='a', age=10)
    print(tc._table_schema.table_name == 'mytable')
    print(tc.age)

    print(f'finished testing schema definitions')
    tc = TestContainer3(1, name='a', age=10)
    print(tc)

if __name__ == '__main__':
    test_new_connectengine()
    test_sqlalchemy_table()
    test_new_doctable()
    test_query()
    test_schema_definitions()
        