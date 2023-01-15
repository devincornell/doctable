import random
from time import time
import datetime
import functools

import sys
sys.path.append('..')
import typing
import doctable
import sqlalchemy
import pytest

@doctable.schema
class MyObj:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    added: datetime.datetime = doctable.AddedCol()

    _indices_ = [
        doctable.Index('ind_name', 'name'),
        doctable.Index('ind_added', 'added'),
        doctable.Index('ind_name_added', 'name', 'added', unique=True),
    ]

    
def test_select_iter_basic():
    tab = doctable.DocTable(target=':memory:', schema=MyObj)
    print(tab.schema_table())
    
    print(tab.engine.inspect().get_indexes(tab.tabname))
    print(tab.indices())
    


    
    
if __name__ == '__main__':
    
    # basic select using different query types
    test_select_iter_basic()
    
    