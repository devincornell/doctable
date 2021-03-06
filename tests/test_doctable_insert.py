
import random
from time import time


import sys
sys.path.append('..')
import doctable


################## Basic Schemas to Test ######################

schema1 = (
    ('integer','id',dict(primary_key=True)),
    ('string', 'title',dict(unique=True)),
    ('integer', 'year',),
)

def gen_data_iter1(n=20):
    for i in range(n):
        yield {
            'title':'doc_{}'.format(i),
            'year':random.randint(1800,2020),
        }
        
def gen_data1(n=20):
    return list(gen_data_iter1(n))



############ FOR CONSISTENCY CHECKING ################

def check_db(rows, db, filt_func=lambda x: True, show=True):
    for r1,r2 in zip(rows,db.select()):
        if show: print(r1,r2)
        for cn in r1.keys():
            if r1[cn] != r2[cn]:
                return False
    return True


############ TESTING INSERT BASIC ################

def test_insert_single1(n=20):
    rows = gen_data1(n)
    db = doctable.DocTable(target=':memory:', schema=schema1)
    for r in rows:
        db.insert(r)
    
    assert(check_db(rows,db,show=False))

def test_insert_many1(n=20):
    rows = gen_data1(n)
    db = doctable.DocTable(target=':memory:', schema=schema1)
    db.insert(rows)
    assert(check_db(rows,db,show=False))


if __name__ == '__main__':
    test_insert_single1()
    test_insert_many1()


    print('all tests completed successfully')
