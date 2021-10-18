import random
from time import time


import sys
#sys.path.append('../..')
sys.path.append('..')
import doctable

def make_db():
    schema = (
        ('integer','id',dict(primary_key=True)),
        ('string', 'title',dict(unique=True)),
        ('float', 'age'),
    )
    return doctable.DocTable(target=':memory:', schema=schema)
    

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
    #db = make_db(fname='db/tb3.db')
    db = make_db()
    print(db)
    
    print('inserting')
    usecols = ('title','age')
    for dr in dictrows:
        db.insert({c:dr[c] for c in usecols})
        
    print('query title')
    for dr,title in zip(dictrows,db.select(db['title'],orderby=db['id'].asc())):
        #print(dr['title'] , title)
        assert(dr['title'] == title)
        
    print('query two')
    for dr,row in zip(dictrows,db.select([db['title'],db['age']],orderby=db['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])
        
    print('query all')
    for dr,row in zip(dictrows,db.select(orderby=db['id'].asc())):
        #print(dr['title'] , row['title'])
        assert(dr['title'] == row['title'])
        assert(dr['age'] == row['age'])

    print(f'query by id')
    k = 5
    test_ids = db.select('id', limit=k)
    selected_rows = db.select_from_set('id', test_ids, cols='id')
    print(selected_rows)
    assert(len(set(selected_rows)) == k)
    
    print('query one, check num results (be sure to start with empty db)')
    assert(len(list(db.select())) == len(dictrows))
    assert(len(list(db.select(limit=1))) == 1)
    
    print('checking single aggregate function')
    sum_age = sum([dr['age'] for dr in dictrows])
    s = db.select_first(db['age'].sum)
    assert(s == sum_age)
    
    
    print('checking multiple aggregate functions')
    sum_age = sum([dr['age'] for dr in dictrows])
    sum_id = sum([i+1 for i in range(len(dictrows))])
    s = db.select_first([db['age'].sum.label('agesum'), db['id'].sum.label('idsum')])
    assert(s['agesum'] == sum_age) #NOTE: THE LABEL METHODS HERE ARENT ASSIGNED TO OUTPUT KEYS
    assert(s['idsum'] == sum_id)
    
    print('checking complicated where')
    ststr = 'user+_3'
    ct_titlematch = sum([dr['title'].startswith(ststr) for dr in dictrows])
    s = db.count(where=db['title'].like(ststr+'%'))
    assert(s == ct_titlematch)
    
    print('running conditional queries')
    minage = db.select_first(db['age'].min)
    maxid = db.select_first(db['id'].max)
    whr = (db['age'] > minage) & (db['id'] < maxid)
    s = db.select_first(db['age'].sum, where=whr)
    sumage = sum([dr['age'] for dr in dictrows[:-1] if dr['age'] > minage])
    assert(s == sumage)
    
    print('selecting right number of elements with negation')
    maxid = db.select_first(db['id'].max)
    s = db.count(where=~(db['id'] < maxid))
    assert(s == 1)
    
    print('selecting specific rows')
    s = db.count(where=db['id'].in_([1,2]))
    assert(s == 2)
    
    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    