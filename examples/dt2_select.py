import random
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
from doctable import DocTable2


schema = (
    ('id','integer',dict(primary_key=True, autoincrement=True)),
    ('name','string', dict(nullable=False)),
    ('age','integer'),
)

if __name__ == '__main__':
    db = DocTable2(schema, verbose=True)
    # defaults:
    #fname=':memory:', engine='sqlite', persistent_conn=True, new_db=True
    
    # insert random docs for testing
    N = 10
    for i in range(N):
        db.insert({'name':'user_'+str(i), 'age':random.random()}, verbose=False)
    print(db)
    
    ############## Regular Select Method #################
    print('============= regular selects ======================\n')
    
    # prints first row
    s = db.select(limit=1)
    print(s,end='\n\n') # [{'id': 1, 'name': 'user_0', 'age': 0.9698034764573769}]
    
    # prints first row, just id and name cols
    s = db.select([db['id'],db['name']], limit=1)
    print(s,end='\n\n') # [{'id': 1, 'name': 'user_0', 'age': 0.9698034764573769}]
    
    exit()
    # print first row of table
    s = db.select_first()
    print(s) # {'_fk_special_': 1, 'id': 1, 'name': 'user_0', 'age': 0.676430343554933}
    
    # get row where id == 2
    s = db.select_first(where=db['id']==2)
    print(s) # {'_fk_special_': 2, 'id': 2, 'name': 'user_1', 'age': 0.875939623410376}
    
    # get count of rows above average
    ages = db.select(db['age']) # list of ages
    age_mean = sum(ages)/len(ages)
    s = db.select([db['id'],db['name']], where=db['age']>age_mean)
    print(s) # [{'id': 3, 'name': 'user_2'}, {'id': 4, 'name': 'user_3'}]
    
    # get two specific rows
    s = db.select([db['name'],db['id']],where=db['id'].in_([1,2]))
    print(s) # [{'name': 'user_0', 'id': 1}, {'name': 'user_1', 'id': 2}]
    
    # select with a relabel
    s = db.select_first([db['age'].label('myage')])
    print(s) # {'myage': 0.003745668183779638, '_fk_special_': 1}
    
    ############## Count Method #################
    print('count methd')
    
    # try simple count
    # since select arg is not sequence, returns list of single items
    s = db.count()
    print(s) # 5
    
    s = db.count(db['age']>0.5)
    print(s) # {'ct': 5}
    
    # get count of rows where age is above average
    ages = db.select(db['age']) # list of ages
    age_mean = sum(ages)/len(ages)
    s = db.count(where=db['age']>age_mean)
    print(s) # 3
    
    # count rows that meet complex compound conditional
    s = db.count(where=(db['age']>age_mean) & ((db['id']<=2) | (db['id']>3)))
    print(s) # 2
    
    # count rows that meet compound conditional
    s = db.count(where=(db['age']>age_mean) & (db['id']>1))
    print(s) # 2
    
    ############## Column Function Bindings #################
    print('column function bindings')
    s = db.select_first(db['age'].max)
    print(s) # (0.9234,) 
    
    s = db.select_first(db['age'].sum)
    print(s) # (2.5428,)
    
    
    ############## Column Operator Bindings #################
    print('selecting based on bound sqlalchemy operators')
    
    s = db.count(db.and_(db['age']>0.2, db['id']>1))
    print(s) # 2
    
    s = db.count(db.or_(db['age']>0.2, db['id']>1))
    print(s) # 2
    
    s = db.select_first(db.not_(db['age']>0.2))
    print(s) # 2
    
    ############## Pandas Series Select #################
    print('selecting as pandas objects')
    
    s = db.select_series(db['age'])
    print(s.var())
    
    df = db.select_df()
    print(df.head(1))
    
    df['morehalf'] = df['age'] > df['age'].mean()
    
    df_agged = df.groupby('morehalf').agg(**{
        'first_name':pd.NamedAgg(column='name', aggfunc='first'),
        'last_name':pd.NamedAgg(column='name', aggfunc='last'),
        'var_age':pd.NamedAgg(column='age', aggfunc=np.var),
        'min_age':pd.NamedAgg(column='age', aggfunc='min'),
        'av_age':pd.NamedAgg(column='age', aggfunc=np.mean),
    })
    print(df_agged)
    
    
    
    
    