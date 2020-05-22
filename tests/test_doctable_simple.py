import random


import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt

def new_db():
    db = dt.DocTable(schema=(
        ('integer', 'id',dict(primary_key=True)),
        ('string', 'title', dict(unique=True)),
        ('integer', 'year'),
    ))
    return db


def gen_data(n=20):
    rows = list()
    for i in range(n):
        rows.append({
            'title':'doc_{}'.format(i),
            'year':random.randint(1800,2020),
        })
    return rows


def test_insert_single1(n=20):
    db = new_db()
    rows = gen_data(n)
    for r in rows:
        db.insert(r)
    for r,dbr in zip(rows,db.select()):
        dbr = dict(dbr)
        del dbr['id']
        assert(dict(dbr)==r)

def test_insert_many1(n=20):
    db = new_db()
    rows = gen_data(n)
    db.insert(rows)
    
    for r,dbr in zip(rows,db.select()):
        dbr = dict(dbr)
        del dbr['id']
        assert(dict(dbr)==r)

if __name__ == '__main__':
    pass

    


