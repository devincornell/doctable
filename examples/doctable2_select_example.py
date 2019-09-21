import random

import sys
sys.path.append('..')
from doctable import DocTable2, func, op

class MyDocuments(DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False)),
        ('age','integer'),
    )
    
    def __init__(self, fname=':memory:', engine='sqlite', verbose=False):
        super().__init__(
            self.schema, 
            tabname=self.tabname, 
            fname=fname,
            engine=engine,
            verbose=verbose,
        )
    
    
    
if __name__ == '__main__':
    md = MyDocuments()
    
    # insert random docs
    N = 50
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print(md)
    
    # try simple count
    # since select arg is not sequence, returns list of single items
    s = md.select(func.count())
    print(s) # [5]
    
    # since count is in a list, will return as list of dicts
    s = md.select([func.count()])
    print(s) # [{'count_1': 5}] ###WEIRD STUFF HERE
    
    # prints first row
    s = md.select(limit=1)
    print(s) # [{'id': 1, 'name': 'user_0', 'age': 0.9698034764573769}]
    
    # print first row of table
    s = md.select_first()
    print(s) # {'_fk_special_': 1, 'id': 1, 'name': 'user_0', 'age': 0.676430343554933}
    
    # get row where id == 2
    s = md.select_first(where=md['id']==2)
    print(s) # {'_fk_special_': 2, 'id': 2, 'name': 'user_1', 'age': 0.875939623410376}
    
    # get count of rows above average
    ages = md.select(md['age']) # list of ages
    age_mean = sum(ages)/len(ages)
    s = md.select([md['id'],md['name']], where=md['age']>age_mean)
    print(s) # [{'id': 3, 'name': 'user_2'}, {'id': 4, 'name': 'user_3'}]
    
    # count rows that meet compound conditional
    s = md.select_first(func.count(), where=(md['age']>age_mean) & (md['id']>1))
    print(s) # 2
    
    # count rows that meet complex compound conditional
    s = md.select_first(func.count(), where=(md['age']>age_mean) & ((md['id']<=2) | (md['id']>3)))
    print(s) # 2
    
    # get count of rows where age is above average
    s = md.select_first(func.count(), where=md['age']>age_mean)
    print(s) # 3
    
    # get sum of ages
    s = md.select_first(func.sum(md['age']))
    print(s) # 2.632576185367908
    
    # get two specific rows
    s = md.select([md['name'],md['id']],where=md['id'].in_([1,2]))
    print(s) # [{'name': 'user_0', 'id': 1}, {'name': 'user_1', 'id': 2}]
    
    
    # select with a relabel
    s = md.select_first([md['age'].label('myage')])
    print(s) # {'myage': 0.003745668183779638, '_fk_special_': 1}
    
    
    s = md.select_first([func.count().label('ct')])
    print(s) # {'ct': 5, '_fk_special_': 5}