import datetime
import os
import sys
sys.path.append('..')
import doctable
import sqlalchemy

import dataclasses



def test_new_connectcore(test_fname: str = 'test.db'):
    if os.path.exists(test_fname):
        os.remove(test_fname) # clean for test
        
    # can't open a non-existent database using open_existing
    try:
        doctable.ConnectCore.open_existing(
            target=test_fname, 
            dialect='sqlite',
        )
        raise Exception('Should have raised FileNotFoundError.')
    except FileNotFoundError as e:
        #print(e)
        pass
    
    # create a new database from scratch
    ce = doctable.ConnectCore.open_new(
        target = test_fname, 
        dialect='sqlite',
        echo = True,
    )

def test_execute(test_fname: str = 'test2.db', table_name: str = 'mytable'):
    if os.path.exists(test_fname):
        os.remove(test_fname) # clean for test
        
    ce = doctable.ConnectCore.open_new(
        target = test_fname, 
        dialect='sqlite',
        echo = True,
    )
    ce.execute(f'CREATE TABLE {table_name} (id int, name text);')
    assert(ce.execute(f'SELECT * FROM {table_name};').fetchall() == [])
    ce.enable_foreign_keys()
    
def test_newtable_and_insepct(test_fname: str = 'test3.db', table_name: str = 'mytable'):
    if os.path.exists(test_fname):
        os.remove(test_fname) # clean for test
        
    ce = doctable.ConnectCore.open_new(
        target = test_fname, 
        dialect='sqlite',
        echo = True,
    )
    try:
        ce.reflect_sqlalchemy_table(table_name)
        raise ValueError('Should have raised TableDoesNotExistError.')
    except doctable.TableDoesNotExistError as e:
        pass
    
    ce.create_sqlalchemy_table(
        table_name = table_name, 
        columns = [
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('name', sqlalchemy.String),
        ],
    )
    ce.create_all_tables()
    ce.reflect_sqlalchemy_table(table_name)
    assert(ce.inspect_table_names() == [table_name])
    assert(ce.inspect_indices(table_name) == [])
    assert(len(ce.inspect_columns(table_name)) == 2)
    
    try:
        ce.create_sqlalchemy_table(
            table_name = table_name,
            columns = [
                sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
                sqlalchemy.Column('age', sqlalchemy.Integer),
            ],
        )
        raise ValueError('Should have raised TableAlreadyExistsError.')
    except doctable.TableAlreadyExistsError as e:
        pass

    ce.extend_sqlalchemy_table(
        table_name = table_name,
        columns = [
            sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True, autoincrement=True),
            sqlalchemy.Column('age', sqlalchemy.Integer),
        ],
    )
    assert(len(ce.inspect_columns(table_name)) == 2)

if __name__ == '__main__':
    test_new_connectcore()
    test_execute()
    test_newtable_and_insepct()
        