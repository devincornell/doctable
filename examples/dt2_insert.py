
import random
import sqlalchemy
from time import time


import sys
sys.path.append('..')
from doctable import DocTable2, func, op

class MyDocuments(DocTable2):
    tabname = 'mydocuments'
    schema = (
        ('id','integer',dict(primary_key=True, autoincrement=True)),
        ('name','string', dict(nullable=False, unique=True)),
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
    
    N = 5
    
    # insert one at a time
    md = MyDocuments()
    st = time()
    for i in range(N):
        md.insert({'name':'user_'+str(i), 'age':random.random()})
    print('took {} sec to load one at a time'.format(time()-st),md) # <DocTable2::mydocuments ct: 5>
    
    # create generator function, which is an iterator
    def get_ages(N):
        for i in range(N):
            yield {'name':'user_'+str(i), 'age':random.random()}
    
    # insert row elements as an iterator
    md = MyDocuments()
    age_iter = get_ages(N)
    st = time()
    md.insert(age_iter)
    print('took {} sec to load from iterator'.format(time()-st),md) # <DocTable2::mydocuments ct: 5>
            
    # insert large list of items
    md = MyDocuments()
    rows = [{'name':'user_'+str(i), 'age':random.random()} for i in range(N)]
    st = time()
    md.insert(rows)
    print('took {} sec to load from list'.format(time()-st),md) # <DocTable2::mydocuments ct: 5>
    
    #now insert somethign which goes against uniqueness constraint
    try:
        md.insert({'name':'user_0', 'age':12})
    except sqlalchemy.exc.IntegrityError:
        print('successfully threw error for breaking uniquenes constraint')
    else:
        raise KeyError('Insert against uniqueness constraint did '
            'not throw exception.')
    
    # CAN'T SOLVE "IF NOT UNIQUE" YET. NEED TO FIGURE OUT A GOOD WAY
    if False:
        # now insert ignoring since the new entry violates uniqueness constraings
        ins = md.insert({'name':'user_0', 'age':-15}, ifnotunique='ignore')
        s = md.select_first(where=md['name']=='user_0')
        print(s['age'], md) # not -15 (whatever value was previously assigned)

        # now insert by replacing
        md.insert({'name':'user_0', 'age':-15}, ifnotunique='replace')
        s = md.select_first(where=md['name']=='user_0')
        print(s['age'], md) # should be -15

        # now insert by replacing
        md.insert([{'name':'user_0', 'age':17}], ifnotunique='replace')
        s = md.select_first(where=md['name']=='user_0')
        print(s['age'], md) # should be 17
    
    