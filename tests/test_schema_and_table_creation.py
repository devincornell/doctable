import datetime
import os
import sys
sys.path.append('..')
import doctable
import sqlalchemy

import dataclasses
@dataclasses.dataclass
class TestDataClass:
    id: int = None
    name: str = None
    age: int = None

def dummy_container(table_name: str = 'test') -> doctable.Container:
    @doctable.table_schema(table_name=table_name)
    class TestContainer:
        name: str
        age: int
        id: int = doctable.Column(column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True))

    return TestContainer

def dummy_container2(table_name: str = 'test'):
    
    @doctable.table_schema(
        table_name=table_name,
        indices = {f'{table_name}_age_name_index': doctable.Index('age', 'name')},
    )
    class DummyContainer:
        name: str
        age: int
        id: int = doctable.Column(
            column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
        )
        updated: datetime.datetime = doctable.Column(
            column_args=doctable.ColumnArgs(
                default=datetime.datetime.utcnow, 
                onupdate=datetime.datetime.utcnow
            )
        )
    
    return DummyContainer

def dummy_schema(table_name: str = 'test'):    
    return doctable.TableSchema(
        table_name=table_name,
        container_type = TestDataClass,
        columns = [
            doctable.ColumnInfo.default('id', int),
            doctable.ColumnInfo.default('name', str),
            doctable.ColumnInfo.default('age', int),
        ],
        indices = [
            doctable.IndexInfo(f'{table_name}_age_index', params=doctable.IndexParams.default('age')),
        ],
        constraints = [],
        table_kwargs = {},
        name_mappings = {'id': 'id', 'name': 'name', 'age': 'age'}
    )

def test_new_doctable(test_table: str = 'test'):
    ce = doctable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )

    try:
        doctable.ReflectedDBTable.from_existing_table(test_table, core=ce)
        raise Exception('Should have raised TableDoesNotExistError.')
    except doctable.TableDoesNotExistError as e:
        print(e)

    #t = doctable.DocTable.from_schema(dummy_schema(), core=ce)
    container = dummy_container(test_table)
    print(dir(container), container)
    #with ce.emit_ddl() as emitter:
    #    t = emitter.create_table(container)
    t = ce.begin_ddl().create_table(container)
    ce.create_all_tables()
    print(t)
    print(ce.inspect_table_names())


    # make sure table hasn't been created yet
    try:
        ce.inspect_columns('nonexistant_table')
        raise Exception('Should have raised NoSuchTableError.')
    except sqlalchemy.exc.NoSuchTableError as e:
        print(e)

    # create the table
    ce.create_all_tables()
    print(ce.inspect_columns(test_table))
    print(ce.inspect_indices(test_table))

    ce = doctable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )
    #print(dummy_container2())

    # now use the awesome context manager
    with ce.begin_ddl() as emitter:
        #t1 = doctable.DocTable.from_schema(dummy_schema('t1'), ce)
        #t2 = doctable.DocTable.from_schema(dummy_schema('t2'), ce)
        t1 = emitter.create_table(dummy_container('t1'))
        t2 = emitter.create_table(dummy_container2('t2'))
    print(t1, t2)
    print(ce.inspect_table_names())
    assert(len(ce.inspect_table_names()) == 2)



######################################################################
def test_ddl(tabname: str = 'mytable1'):

    core = doctable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )

    import datetime
    @doctable.table_schema(table_name=tabname)
    class MyContainer1:
        name: str
        age: int
        id: int = doctable.Column(
            column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
        )
        updated: datetime.datetime = doctable.Column(
            column_args=doctable.ColumnArgs(default=datetime.datetime.utcnow),
        )
        added: datetime.datetime = doctable.Column(
            column_args=doctable.ColumnArgs(
                default=datetime.datetime.utcnow, 
                onupdate=datetime.datetime.utcnow
            )
        )

    with core.begin_ddl() as emitter:
        tab1 = emitter.create_table_if_not_exists(container_type=MyContainer1)
    #print(core.inspect_columns(tabname))
    o = MyContainer1(name='John Doe', age=30)
    print(o)
    with tab1.query() as q:
        q.insert_single(o)
        print(q.select())

######################################################################

def test_schema_definitions():

    @doctable.table_schema
    class TestContainer0:
        id: int = None
        name: str = None
        age: int = None

    assert(dataclasses.is_dataclass(TestContainer0))
    assert(doctable.SCHEMA_ATTRIBUTE_NAME in dir(TestContainer0))
    schema = getattr(TestContainer0, doctable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'TestContainer0')

    # test the most basic usage
    @doctable.table_schema()
    class TestContainer1:
        id: int
        name: str
        age: int

    assert(dataclasses.is_dataclass(TestContainer1))
    assert(doctable.SCHEMA_ATTRIBUTE_NAME in dir(TestContainer1))
    schema = doctable.get_schema(TestContainer1)
    assert(schema.table_name == 'TestContainer1')

    # make sure the arguments work with it
    if sys.version_info.minor >= 10:
        doctable.table_schema(TestDataClass, slots=True)
    else:
        try:
            doctable.table_schema(TestDataClass, slots=True)
            raise Exception('Should have raised TypeError.')
        except TypeError as e:
            #print(e)
            pass

    @doctable.table_schema(
        indices = {
            'age_index': doctable.Index('age'),
        },
    )
    class TestContainer2:
        name: str
        age: int
        id: int = doctable.Column(
            column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
        )
        
    
    assert(dataclasses.is_dataclass(TestContainer2))
    assert(doctable.SCHEMA_ATTRIBUTE_NAME in dir(TestContainer2))
    schema = getattr(TestContainer2, doctable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'TestContainer2')
    
    @doctable.table_schema(
        table_name='mytable',
    )
    class TestContainer3:
        name: str
        age: int
        id: int = doctable.Column(column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True))
    
    schema = getattr(TestContainer3, doctable.SCHEMA_ATTRIBUTE_NAME)
    assert(schema.table_name == 'mytable')

    tc = TestContainer3(id=1, name='a', age=10)
    print(tc._table_schema.table_name == 'mytable')
    print(tc.age)

    print(f'finished testing schema definitions')
    tc = TestContainer3(name='a', age=10)
    print(tc)
    

if __name__ == '__main__':
    test_ddl()
    test_new_doctable()
    test_schema_definitions()
    
    