import pickle
import random
from collections import Counter
import os

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt
import pytest

        
def divide_by_two(el, dividend):
    return el//dividend
    
def test_distribute_chunk_process():
    # tests DocParser._distribute_chunk_process
    
    # make test set
    dividend = 3
    elements = list(range(100))
    
    true_parsed = [divide_by_two(el, dividend) for el in elements]

    # run distributed parser
    parsed = dt.DocParser._distribute_chunk_process(elements, divide_by_two, dividend, n_cores=3)
    assert(all([elt==el for elt,el in zip(true_parsed,parsed)]))
    

    
def divide_and_insert(el, db, dividend):
    ## divides el by divident, inserting in db
    res = el//dividend
    db.insert({'result':res})
    
def test_distribute_chunk_process_store():
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
    parsed = dt.DocParser._distribute_chunk_process_store(elements, divide_and_insert, db, dividend, n_cores=3)
    parsed = db.select('result')
    parsed_cts = Counter(parsed)
    
    # compare frequency counts of stored data with actual data
    assert(len(parsed_cts) == len(true_parsed_cts))
    assert(all([true_parsed_cts[num]==ct for num,ct in parsed_cts.items()]))
    
    # clean up
    if os.path.exists(fname):
        os.remove(fname)
    

if __name__ == '__main__':
    test_distribute_chunk_process_store()
    #test_distribute_chunk_process()


