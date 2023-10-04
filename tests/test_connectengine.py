
import sys
sys.path.append('..')
import newtable
import sqlalchemy

if __name__ == '__main__':
    ce = newtable.ConnectEngine.new(target=':memory:', dialect='sqlite')
    print(ce)
    
    tab = ce.new_sqlalchemy_table(
        table_name='test',
        columns=[
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('name', sqlalchemy.String),
            sqlalchemy.Column('age', sqlalchemy.Integer),
            sqlalchemy.Index('age_index', 'age'),
        ],
    )
    print(tab)

    tab2 = ce.new_sqlalchemy_table(
        table_name='test',
        columns=[
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
            sqlalchemy.Column('whatever', sqlalchemy.String),
        ],
    )

    print(sqlalchemy.inspect(tab).columns)
    print(sqlalchemy.inspect(tab2).columns)

