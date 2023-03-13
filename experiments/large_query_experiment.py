import random
from time import time
import datetime

import sys
sys.path.append('..')
import doctable

@doctable.schema
class TestSchema:
    __slots__ = []
    _id: int = doctable.IDCol()
    age: int = doctable.Col()
    added: datetime.datetime = doctable.AddedCol()

def test_large_query():
    tab = doctable.DocTable(schema=TestSchema, target=':memory:')
    print(tab)
    tab.q.insert_multi_raw([{'age':-1} for _ in range(100000)])
    
    tab.q.select(where=tab['age'].in_(list(range(10000000))), verbose=True)

    
    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_large_query()
    
    