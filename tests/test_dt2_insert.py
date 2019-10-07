
import random
from time import time

import test_dt2_helper as th

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt

############ TESTING INSERT BASIC ################

def test_insert_single1(n=20):
    rows = th.gen_data1(n)
    db = dt.DocTable2(th.schema1)
    for r in rows:
        db.insert(r)
    
    assert(th.check_db(rows,db,show=False))

def test_insert_many1(n=20):
    rows = th.gen_data1(n)
    db = dt.DocTable2(th.schema1)
    db.insert(rows)
    assert(th.check_db(rows,db,show=False))


if __name__ == '__main__':
    test_insert_single1()
    test_insert_many1()


    print('all tests completed successfully')
