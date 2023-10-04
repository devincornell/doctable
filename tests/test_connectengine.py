
import sys
sys.path.append('..')
import newtable
import sqlalchemy

if __name__ == '__main__':
    ce = newtable.ConnectEngine.new(target=':memory:', dialect='sqlite')
    print(ce)
    
    try:
        tab0 = ce.reflect_existing_table(table_name='test')
    except newtable.connectengine.TableDoesNotExistError as e:
        print(e)
    
    tab1 = ce.new_sqlalchemy_table(
        table_name='test',
        columns=[
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('name', sqlalchemy.String),
            sqlalchemy.Column('age', sqlalchemy.Integer),
            sqlalchemy.Index('age_index', 'age'),
        ],
    )
    print(tab1)

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

    tab3 = ce.reflect_existing_table(
        table_name='test',
    )
    
    tab4 = ce.reflect_existing_table(table_name='test')
    tab5 = ce.reflect_existing_table(table_name='test')

    print(sqlalchemy.inspect(tab1).columns)
    print(sqlalchemy.inspect(tab3).columns)

