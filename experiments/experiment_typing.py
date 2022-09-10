#from __future__ import annotations

from typing import Union, Mapping, Sequence, Tuple, Set, List
from dataclasses import dataclass#, field, fields
import datetime
import pandas as pd

import sqlalchemy

import sys
sys.path.append('..')
import doctable

@doctable.schema(require_slots=False)
class MySchema:
    _id: int = doctable.IDCol()
    name: str = doctable.Col()

if __name__ == '__main__':
    
    tab = doctable.DocTable(target=':memory:', schema=MySchema)
    tab.insert_single({'name': 'Devin'})
    tab.insert_single({'name': 'Devin'})
    tab.insert_single({'name': 'Carl'})

    print(type(tab.c.name.desc()))
    print(type(tab.c.name))
    
    #orderby=tab['name'].desc()
    print(type(sqlalchemy.sql.select(tab.columns)))
    print(tab.select())
    
    print(tab.schema_table())
