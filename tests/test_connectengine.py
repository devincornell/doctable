import os
import sys
sys.path.append('..')
import newtable
import sqlalchemy

def test_new_sqlalchemy_table(test_fname: str = 'test.db', test_table: str = 'test'):
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
    tab1 = ce.new_sqlalchemy_table(
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
        tab2 = ce.new_sqlalchemy_table(
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

    # essentially just gets the same table object
    tab3 = ce.reflect_sqlalchemy_table(
        table_name=test_table,
    )
    
    # these are going to be the same references
    tab4 = ce.reflect_sqlalchemy_table(table_name=test_table)
    tab5 = ce.reflect_sqlalchemy_table(table_name=test_table)
    assert(tab4 is tab5) # they return the same reference
    
    # you can see the columns are the same
    print(sqlalchemy.inspect(tab1).columns)
    print(sqlalchemy.inspect(tab3).columns)

    # make sure table only created after create_all_tables
    assert(test_table not in ce.inspect_table_names())
    ce.create_all_tables()
    assert(test_table in ce.inspect_table_names())


def dummy_schema() -> newtable.Schema:
    return newtable.Schema(
        table_name='test',
        columns = {
            'id': newtable.ColumnInfo(sqlalchemy.Integer, primary_key=True),
            'name': newtable.ColumnInfo(sqlalchemy.String),
            'age': newtable.ColumnInfo(sqlalchemy.Integer),
        },
        indices = {
            'age_index': newtable.IndexInfo('age'),
        },
        constraints = [],
    )

def test_query():
    ce = newtable.ConnectCore.open_new(
        target = ':memory:', 
        dialect='sqlite',
    )
    with ce.create_tables() as ctx:
        ctx.create_tables(
            table_name='test',
            columns=[
                sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column('name', sqlalchemy.String),
                sqlalchemy.Column('age', sqlalchemy.Integer),
                sqlalchemy.Index('age_index', 'age'),
            ],
        )

    # run a raw query on this baby
    with ce.connect() as conn:
        r = conn.execute(
            sqlalchemy.text(f"INSERT INTO {test_table} (name, age) VALUES (:name, :age)"),
            [{"name": 'a', "age": 1}, {"name": 'b', "age": 4}],
        )

    # alternatively, do the same thing with query()
    with ce.query() as q:
        r = q.execute(
            f"INSERT INTO {test_table} (name, age) VALUES (:name, :age)",
            [{"name": 'a', "age": 1}, {"name": 'b', "age": 4}],
        )
        print(r)

def test_schema():
    @newtable.schema(
        table_name = 'users',
        constraints = [
            sqlalchemy.ForeignKeyConstraint(),
        ],
        indices = [
            sqlalchemy.Index(),
        ]
    )
    def test():
        pass


if __name__ == '__main__':
    test_new_sqlalchemy_table()
    test_query()
        
        
        