import random
from time import time


import sys
sys.path.append('../..')
from doctable import DocTable2, func, op


def make_dt(schema, fname):
    if fname is None:
        dt = DocTable2(schema, verbose=False)
    else:
        dt = DocTable2(schema, verbose=False, fname=fname)
    return dt

def dt_basic(fname=None):
    schema = (
        ('id','integer',dict(primary_key=True)),
        ('title','string', dict(unique=True)),
        ('age','float'),
    )
    return make_dt(schema,fname)

def dt_special(fname=None):
    schema = (
        ('id','integer',dict(primary_key=True)),
        ('title','string', dict(unique=True)),
        ('age','float'),
        ('model','bigblob'),
        ('sents','sentences'),
        ('paragraphs','sentences'),
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
    for dr,title in zip(dictrows,dt.select_iter(dt['title'],orderby=dt['id'].asc())):
        #print(dr['title'] , title)
        assert(dr['title'] == title)
        
    print('query two')
    for dr,row in zip(dictrows,dt.select_iter([dt['title'],dt['age']],orderby=dt['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
        
    print('query all')
    for dr,row in zip(dictrows,dt.select_iter(orderby=dt['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
    
    print('query one, check num results (be sure to start with empty db)')
    assert(len(list(dt.select_iter())) == len(dictrows))
    assert(len(list(dt.select_iter(limit=1))) == 1)
    
    print('checking single aggregate function')
    sum_age = sum([dr['age'] for dr in dictrows])
    s = dt.select_first(func.sum(dt['age']))
    assert(s == sum_age)
    
    
    print('checking multiple aggregate functions')
    sum_age = sum([dr['age'] for dr in dictrows])
    sum_id = sum([i+1 for i in range(len(dictrows))])
    s = dt.select_first([func.sum(dt['age'].label('agesum')), func.sum(dt['id'].label('idsum'))])
    assert(s['sum_1'] == sum_age) #NOTE: THE LABEL METHODS HERE ARENT ASSIGNED TO OUTPUT KEYS
    assert(s['sum_2'] == sum_id)
    
    print('checking complicated where')
    ststr = 'user+_3'
    ct_titlematch = sum([dr['title'].startswith(ststr) for dr in dictrows])
    s = dt.select_first(func.count(dt['title']), where=dt['title'].like(ststr+'%'))
    assert(s == ct_titlematch)
    
    print('running conditional queries')
    minage = dt.select_first(func.min(dt['age']))
    maxid = dt.select_first(func.max(dt['id']))
    whr = (dt['age'] > minage) & (dt['id'] < maxid)
    s = dt.select_first(func.sum(dt['age']), where=whr)
    sumage = sum([dr['age'] for dr in dictrows[:-1] if dr['age'] > minage])
    assert(s == sumage)
    
    print('selecting right number of elements with negation')
    maxid = dt.select_first(func.max(dt['id']))
    s = dt.select_first(func.count(), where=~(dt['id'] < maxid))
    assert(s == 1)
    
    print('selecting specific rows')
    s = dt.select_first(func.count(), where=dt['id'].in_([1,2]))
    assert(s == 2)
    

def test_select_iter_special(n=20):
    datarows, dictrows = generate_data_many(n=n)
    #dt = dt_basic(fname='db/tb4.db')
    dt = dt_special()#fname='db/tb5.db')
    print(dt)
    
    print('inserting')
    for dr in dictrows:
        dt.insert(dr)
    
    print('verifying stored results')
    st = time()
    for dr,row in zip(dictrows,dt.select_iter(orderby=dt['id'].asc())):
        for cn in dr.keys():
            assert(dr[cn] == row[cn])
    print('took {} min to check {} rows using select_iter()'
         ''.format((time()-st)/60,n))
    
def test_select_special(n=20):
    datarows, dictrows = generate_data_many(n=n)
    #dt = dt_basic(fname='db/tb4.db')
    dt = dt_special()#fname='db/tb5.db')
    print(dt)
    
    print('inserting')
    for dr in dictrows:
        dt.insert(dr)
    
    print('checking data consistency')
    st = time()
    for dr,row in zip(dictrows,dt.select(orderby=dt['id'].asc())):
        for cn in dr.keys():
            assert(dr[cn] == row[cn])
    print('took {} min to check {} rows using select()'
         ''.format((time()-st)/60,n))
    
    
    
    
    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    # compare time select() should be faster than select_iter()
    # because select_iter queries data columns one-per-query.
    # On the other hand, select_iter should have smaller memory
    # overhead.
    n = 20
    test_select_iter_special(n)
    test_select_special(n)
    
    