
import sys
sys.path.append('..')
import newtable
import sqlalchemy

def test_new_sqlalchemy_table():
    ce = newtable.ConnectEngine.connect(
        target='test.db', 
        dialect='sqlite',
        echo=True,
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

def test_query():
    pass


if __name__ == '__main__':
    test_new_sqlalchemy_table()
        
        
        
        