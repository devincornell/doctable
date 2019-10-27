




import random


import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt
import pytest

import os
    
    
    
def test_init_errors():
    fname = 'tmp.db'
    
    if os.path.exists(fname):
        os.remove(fname)
    
    db = dt.DocTable(fname=fname, colschema=(
        'id integer primary key autoincrement',
        'number integer',
    ))

    N = 100
    [db.add({'number':0}, verbose=False) for _ in range(N)]

    print(db.getdf(['id']))
    print(db)
    db.delete('id == 5', verbose=True)
    print(db)

    ids = db.getdf(where='number == "0"')['id']
    print(ids)
    
    assert(ids.shape[0] == N-1)
    assert(not 5 in list(ids))
    
    if os.path.exists(db.fname):
        os.remove(db.fname)
    

if __name__ == '__main__':
    pass
