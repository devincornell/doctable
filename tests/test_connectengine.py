import os
import sys
sys.path.append('..')
import newtable
import sqlalchemy

def test_new_sqlalchemy_table(test_fname: str = 'test.db'):
    if os.path.exists(test_fname):
        os.remove(test_fname)
        
    try:
        newtable.ConnectCore.open_existing(
            target=test_fname, 
            dialect='sqlite',
        )
        raise Exception('Should have raised FileNotFoundError.')
    except FileNotFoundError as e:
        print(e)
    
    ce = newtable.ConnectCore.open_new(
        target = test_fname, 
        dialect='sqlite',
    )        
    
    #print(ce)
    #return ce
    try: # database is actually created here
        tab0 = ce.reflect_sqlalchemy_table(table_name='test')
    except newtable.connectengine.TableDoesNotExistError as e:
        print(e)
    #return ce
    tab1 = ce.new_sqlalchemy_table(
        table_name='test',
        columns=[
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('name', sqlalchemy.String),
            sqlalchemy.Column('age', sqlalchemy.Integer),
            sqlalchemy.Index('age_index', 'age'),
        ],
    ) # note that this hasn't created the database table yet
    print(tab1)
    #return ce

    try:
        tab2 = ce.new_sqlalchemy_table(
            table_name='test',
            columns=[
                sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
                sqlalchemy.Column('name', sqlalchemy.String),
            ],
        )
        print(tab2)
        raise Exception('Should have raised TableAlreadyExistsError.')
    except newtable.TableAlreadyExistsError as e:
        print(e)

    tab3 = ce.reflect_sqlalchemy_table(
        table_name='test',
    )
    
    tab4 = ce.reflect_sqlalchemy_table(table_name='test')
    tab5 = ce.reflect_sqlalchemy_table(table_name='test')
    assert(tab4 is tab5) # they return the same reference
    
    # you can see the columns are the same
    print(sqlalchemy.inspect(tab1).columns)
    print(sqlalchemy.inspect(tab3).columns)

    ce.create_all_tables()

def test_query():
    pass

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


if __name__ == '__main__':
    test_new_sqlalchemy_table()
        
        
        
        