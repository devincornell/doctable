
import random

#import sys
#sys.path.append('../..')
#from doctable import DocTable2, func, op


############ TESTING NORMAL DATA (NO SPECIAL COLS) ################

schema1 = (
    ('id','integer',dict(primary_key=True)),
    ('title','string', dict(unique=True)),
    ('year','integer'),
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