import random
from time import time


import sys
sys.path.append('../..')
import doctable as dt


def make_dt(schema, fname):
    if fname is None:
        db = dt.DocTable(schema, verbose=False)
    else:
        db = dt.DocTable(schema, verbose=False, fname=fname)
    return db

def dt_basic(fname=None):
    schema = (
        ('integer','id',dict(primary_key=True)),
        ('string', 'title',dict(unique=True)),
        ('float', 'age'),
    )
    return make_dt(schema,fname)
    

def generate_data(i=0):
    # generated data for a single row
    title = 'user+_' + str(random.randrange(1000,9999)) + str(i)
    age = random.randrange(100,999)/10
    myblob = [1]*1000 + ['woo',]*10
    
    lensent = random.randrange(1,10)
    nsent = random.randrange(3,8)
    mysents = [[str(i) for i in range(lensent)] for _ in range(nsent)]
    mysents2 = mysents + [['a','b','d']]
    
    return title, age, myblob, mysents, mysents2
    
def generate_data_many(n=20):
    datarows = list()
    dictrows = list()
    for i in range(n):
        t,a,b,s,s2 = generate_data(i)
        datarows.append((t,a,b,s,s2))
        dictrows.append({
            'title':t,
            'age':a,
            'model':b,
            'sents':s,
            'paragraphs':s2,
        })
    return datarows, dictrows


def test_select_iter_basic():
    datarows, dictrows = generate_data_many(n=20)
    #dt = dt_basic(fname='db/tb3.db')
    dt = dt_basic()
    print(dt)
    
    print('inserting')
    usecols = ('title','age')
    for dr in dictrows:
        dt.insert({c:dr[c] for c in usecols})
        
    print('query title')
    for dr,title in zip(dictrows,dt.select(dt['title'],orderby=dt['id'].asc())):
        #print(dr['title'] , title)
        assert(dr['title'] == title)
        
    print('query two')
    for dr,row in zip(dictrows,dt.select([dt['title'],dt['age']],orderby=dt['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
        
    print('query all')
    for dr,row in zip(dictrows,dt.select(orderby=dt['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
    
    print('query one, check num results (be sure to start with empty db)')
    assert(len(list(dt.select())) == len(dictrows))
    assert(len(list(dt.select(limit=1))) == 1)
    
    print('checking single aggregate function')
    sum_age = sum([dr['age'] for dr in dictrows])
    s = dt.select_first(dt['age'].sum)
    assert(s == sum_age)
    
    
    print('checking multiple aggregate functions')
    sum_age = sum([dr['age'] for dr in dictrows])
    sum_id = sum([i+1 for i in range(len(dictrows))])
    s = dt.select_first([dt['age'].sum.label('agesum'), dt['id'].sum.label('idsum')])
    assert(s['agesum'] == sum_age) #NOTE: THE LABEL METHODS HERE ARENT ASSIGNED TO OUTPUT KEYS
    assert(s['idsum'] == sum_id)
    
    print('checking complicated where')
    ststr = 'user+_3'
    ct_titlematch = sum([dr['title'].startswith(ststr) for dr in dictrows])
    s = dt.count(where=dt['title'].like(ststr+'%'))
    assert(s == ct_titlematch)
    
    print('running conditional queries')
    minage = dt.select_first(dt['age'].min)
    maxid = dt.select_first(dt['id'].max)
    whr = (dt['age'] > minage) & (dt['id'] < maxid)
    s = dt.select_first(dt['age'].sum, where=whr)
    sumage = sum([dr['age'] for dr in dictrows[:-1] if dr['age'] > minage])
    assert(s == sumage)
    
    print('selecting right number of elements with negation')
    maxid = dt.select_first(dt['id'].max)
    s = dt.count(where=~(dt['id'] < maxid))
    assert(s == 1)
    
    print('selecting specific rows')
    s = dt.count(where=dt['id'].in_([1,2]))
    assert(s == 2)
    
    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    