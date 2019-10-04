
import random

#import sys
#sys.path.append('../..')
#from doctable import DocTable2, func, op


############ TESTING NORMAL DATA (NO SPECIAL COLS) ################

schema_simple = (
    ('id','integer',dict(primary_key=True)),
    ('title','string', dict(unique=True)),
    ('year','integer'),
)

def gen_data_simple_iter(n=20):
    for i in range(n):
        yield {
            'title':'doc_{}'.format(i),
            'year':random.randint(1800,2020),
        }
        
def gen_data_simple(n=20):
    return list(gen_data_simple_iter(n))


############ TESTING SPECIAL DATA ################

schema_special = (
    ('id','integer',dict(primary_key=True)),
    ('title','string', dict(unique=True)),
    ('model','bigpickle'),
    ('sents','subdoc'),
)    
    
    
def gen_data_special_iter(n=20):
    for i in range(n):
        yield {
            'title':'doc_{}'.format(i),
            'model': {'dude':i,'what':'a'},
            'sents': [[str(j) for j in range(random.randint(0,10))]
                      for i in range(random.randint(1,5))]
        }
        
def gen_data_special(n=20):
    return list(gen_data_special_iter(n))



############ FOR CONSISTENCY CHECKING ################

def check_db(rows, db, filt_func=lambda x: True, show=True):
    for r1,r2 in zip(rows,db.select()):
        if show: print(r1,r2)
        for cn in r1.keys():
            if r1[cn] != r2[cn]:
                return False
    return True
#def make_dt(schema, fname):
#    if fname is None:
#        dt = DocTable2(schema, verbose=False)
#    else:
#        dt = DocTable2(schema, verbose=False, fname=fname)
#    return dt
