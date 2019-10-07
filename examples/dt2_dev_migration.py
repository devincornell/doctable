import random
from pprint import pprint

import sys
sys.path.append('..')
import doctable as dt


schema1 = (
    ('id','integer',dict(primary_key=True, autoincrement=True)),
    ('name','string', dict(nullable=False, unique=True)),
)

schema2 = (
    ('id','integer',dict(primary_key=True, autoincrement=True)),
    ('name','string', dict(nullable=False, unique=True)),
    ('age','integer',dict(comment='Hahaha this is my comment.')),
)


if __name__ == '__main__':
    olddb = 'tmp_old_migrate_{}.db'.format(random.random())
    newdb1 = 'tmp_new_migrate_{}.db'.format(random.random())
    newdb2 = 'tmp_new_migrate_{}.db'.format(random.random())
    
    md1 = dt.DocTable2(schema1, fname=olddb)
    print('next id:', md1.next_id())
    # insert random docs
    N = 50
    for i in range(N):
        md1.insert({'name':'user_'+str(i)})
    print('old table:', md1)
    del md1 # frees connection
    
    # 'age':random.random()
    #md2 = dt.DocTable2(schema2, fname='tmp_new.db')
    dt.migrate_db('tmp_old.db', newdb1,schema2,delcols=['id'])
    print('first new table:', dt.DocTable2(schema2,fname=newdb1))
    
    newcolmap = {
        'age': lambda r: float(r['name'][-1]) + random.random(),
    }
    dt.migrate_db(olddb, newdb2,schema2,newcolmap)
    print('second new table:', dt.DocTable2(schema2,fname=newdb2))
    print(olddb, newdb1, newdb2)
    
    