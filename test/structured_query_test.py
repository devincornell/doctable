import sys
sys.path.append('..')
from doctable import DocTable


q1 = {
    'num':1.2,
    'baby':'baby g',
    'id':(1,2,3),
    'dude':{
        'or':(
            {'>':5},
            {'<':3},
        ),
    }
}
 
q2 = {
    'dude':{
        'or':(
            {'>':5,'<':1},
            {'<':3},
        ),
    }
}
    

def test_make_query(w):
    cols = ('num integer', 'baby VARCHAR', 'id integer', 'dude integer')
    a = DocTable(colschema=cols)
    #print(a.schema)
    
    r = list(a.get('baby',w))
    print(r)

if __name__ == '__main__':
    test_make_query(q1)
    test_make_query(q2)
    