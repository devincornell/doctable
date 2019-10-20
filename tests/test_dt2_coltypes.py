import random
from time import time


import sys
sys.path.append('../..')
import doctable as dt



def random_toks(tmin=1, tmax=3):
    toks = [str(random.randrange(0,99))
            for _ in range(random.randrange(tmin, tmax))
           ]
    return tuple(toks)


def test_tokens(n=100):
    db = dt.DocTable2(schema=(
        ('id', 'integer'),
        ('doc','tokens'),
    ))
    intoks = list()
    for i in range(n):
        toks = random_toks()
        intoks.append(toks)
        db.insert({'doc':toks,'id':i})
    
    for i in range(n):
        toks = db.select_first('doc',where=db['id']==i)
        assert(toks == intoks[i])
    
        
def random_sents(tmin=0, tmax=5):
    sents = tuple([
        tuple([str(random.randrange(10,99))
            for _ in range(random.randrange(tmin,tmax))
        ])
        for _ in range(random.randrange(tmin, tmax))
    ])
    return sents
        
def test_subdocs(n=100):
    db = dt.DocTable2(schema=(
        ('id', 'integer'),
        ('sents','tokens'),
    ))
    insents = list()
    for i in range(n):
        sents = random_sents()
        print(sents)
        insents.append(sents)
        db.insert({'sents':sents,'id':i})
    
    for i in range(n):
        sents = db.select_first('sents',where=db['id']==i)
        assert(sents == insents[i])
    

def random_paragraphs(tmin=0, tmax=20):
    pars = tuple([
        tuple([
            tuple([str(random.randrange(10,99)) for _ in range(random.randrange(tmin,tmax))])
            for _ in range(random.randrange(tmin,tmax))
        ])
        for _ in range(random.randrange(tmin, tmax))
    ])
    return pars
        
def test_subsubdocs(n=100):
    db = dt.DocTable2(schema=(
        ('id', 'integer'),
        ('pars','tokens'),
    ))
    inpars = list()
    for i in range(n):
        pars = random_paragraphs()
        inpars.append(pars)
        db.insert({'pars':pars,'id':i})
    
    for i in range(n):
        pars = db.select_first('pars',where=db['id']==i)
        assert(pars == inpars[i])
    
    
    
if __name__ == '__main__':
    
    pass
    