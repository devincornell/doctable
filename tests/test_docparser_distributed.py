import pickle
import random
from collections import Counter
import os

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt
import pytest
import spacy

        
def divide_by_two_multi(numbers, dividend):
    return [num//dividend for num in numbers]
    
def test_distribute_chunks():
    # tests DocParser._distribute_chunk_process
    
    # make test set
    dividend = 3
    elements = list(range(1000))
    
    true_parsed = divide_by_two_multi(elements, dividend)

    # run distributed parser
    parsed = dt.DocParser.distribute_chunks(divide_by_two_multi, elements, dividend, n_cores=4)
    assert(all([elt==el for elt,el in zip(true_parsed,parsed)]))
    
    
def divide_by_two(num, dividend):
    return num//dividend
    
def test_distribute_process():
    # tests DocParser._distribute_chunk_process
    
    # make test set
    dividend = 3
    elements = list(range(1000))
    
    true_parsed = [divide_by_two(el,dividend) for el in elements]

    # run distributed parser
    parsed = dt.DocParser.distribute_process(divide_by_two, elements, dividend, n_cores=4)
    assert(all([elt==el for elt,el in zip(true_parsed,parsed)]))
    

    
def divide_and_insert(el, db, dividend):
    ## divides el by divident, inserting in db
    res = el//dividend
    db.insert({'result':res})
    
def test_distribute_process_store():
    # tests DocParser._distribute_chunk_process
    
    # make new doctable and delete all existing entries
    fname = 'test_dist_chunk_proc_store.db'
    db = dt.DocTable(schema=[('integer','result')],
            fname=fname)
    db.delete()
    
    # make test set
    dividend = 3
    elements = list(range(100))
    true_parsed = [divide_by_two(el, dividend) for el in elements]
    true_parsed_cts = Counter(true_parsed)

    # run distributed parser
    parsed = dt.DocParser.distribute_process(divide_and_insert, elements, dividend, dt_inst=db, n_cores=3)
    parsed = db.select('result')
    parsed_cts = Counter(parsed)
    
    # compare frequency counts of stored data with actual data
    assert(len(parsed_cts) == len(true_parsed_cts))
    assert(all([true_parsed_cts[num]==ct for num,ct in parsed_cts.items()]))
    
    # clean up
    if os.path.exists(fname):
        os.remove(fname)
        
        
        
def tokenize_and_insert(doc, db):
    toks = dt.DocParser.tokenize_doc(doc)
    db.insert({'result':toks})
        
def test_distribute_parse():
    # tests DocParser._distribute_chunk_process
    
    # make new doctable and delete all existing entries
    fname = 'test_dist_parse.db'
    db = dt.DocTable(schema=[('pickle','result')],
            fname=fname)
    db.delete()
    
    # make test set
    texts = [' '.join([str(j*i) for j in range(10)]) for i in range(100)]
    true_parsed_cts = Counter([tuple(t.split()) for t in texts])
    
    # run distributed parser
    nlp = spacy.load('en', disable=['ner','tagger'])
    
    print('starting parsing (actually takes a long time)')
    parsed = dt.DocParser.distribute_parse(texts, nlp, n_cores=2, dt_inst=db, parsefunc=tokenize_and_insert)
    
    parsed = db.select('result')
    parsed_cts = Counter(map(tuple,parsed))
    
    # compare frequency counts of stored data with actual data
    #print(parsed_cts)
    #print(true_parsed_cts)
    assert(len(parsed_cts) == len(true_parsed_cts))
    assert(all([true_parsed_cts[num]==ct for num,ct in parsed_cts.items()]))
    
    # clean up
    if os.path.exists(fname):
        os.remove(fname)
    

if __name__ == '__main__':
    test_distribute_chunks()
    test_distribute_process()
    test_distribute_process_store()
    test_distribute_parse()

