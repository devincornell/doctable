import random
from doctable2 import NewDocTable

def schemadt():
    example_schema = (
        ('id','integer',dict(primary_key=True)),
        ('title','string', dict(unique=True)),
        ('age','float'),
        ('model','bigblob'),
        ('sents','sentences')
        ('paragraphs','sentences'),
    )
    
    dt = NewDocTable(example_schema, verbose=False)
    return dt
    

def generate_data(i=0):
    # generated data for a single row
    title = 'user+_' + str(random.randrange(1000,9999)) + str(i)
    age = random.randrange(100,999)/10
    myblob = [1]*1000 + ['woo',]*10
    
    lensent = random.randrange(1,10)
    nsent = random.randrange(3,8)
    mysents = [[str(i) for i in range(lensent)] for _ in range(nsent)]
    mysents2 = mysents + ['a','b','d']
    
    return title, age, myblob, mysents, mysents2
    
def generate_data_many(n=20):
    datrows = list()
    dictrows = list()
    for i in range(n):
        t,a,b,s,s2 = generate_data(i)
        datrows.append(t,a,b,s,s2)
        dictrows.append({
            'title':t,
            'age':a,
            'model':b,
            'sents':s,
            'paragraphs's2,
        })
    return datarows, dictrows


def test_insert():
    
    # test insert data one-by-one
    datarows, dictrows = generate_data_many(n=20)
    dt = schemadt()
    for row in dictrows:
        dt.insert(row)
        rows.append(row)
        
    for sd,r in zip(datarows, dt.select()):
        t,a,b,s,s2 = sd
        assert(r['title'] == t)
        assert(r['age'] == a)
        assert(r['model'] == b)
        assert(r['sents'] == s)
        assert(r['paragraphs'] == s2)
    
    # test insert many with list (already in memory)
    dt = schemadt()
    dt.insert(dictrows)
    for sd,r in zip(datarows, dt.select()):
        t,a,b,s,s2 = sd
        assert(r['title'] == t)
        assert(r['age'] == a)
        assert(r['model'] == b)
        assert(r['sents'] == s)
        assert(r['paragraphs'] == s2)
    
    # test insert many with iter (not list, can't assum in memory)
    dt = schemadt()
    dt.insert(iter(dictrows))
    for sd,r in zip(datarows, dt.select()):
        t,a,b,s,s2 = sd
        assert(r['title'] == t)
        assert(r['age'] == a)
        assert(r['model'] == b)
        assert(r['sents'] == s)
        assert(r['paragraphs'] == s2)
    
def test_select():
    
    datarows, dictrows = generate_data_many(n=20)
    
    dt = schemadt()
    dt.insert(dictrows)
    
    # test basic dictionary select
    ids = list(range(len(datarows)))
    
    
    
    
    
    
    
if __name__ == '__main__':
    test_insert()
    
    