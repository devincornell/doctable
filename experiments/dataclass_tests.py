from typing import Union, Mapping, Sequence, Tuple, Set, List
from dataclasses import dataclass#, field, fields
import datetime
import pandas as pd

import sys
sys.path.append('..')
import doctable


@dataclass
class MyClass(doctable.DocTableRow):
    name: str = doctable.Col(unique=True)

    # builtin column types
    idx: int = doctable.IDCol()
    updated: datetime.datetime = doctable.UpdatedCol()
    added: datetime.datetime = doctable.AddedCol()

    # custom column types 
    lon: float = doctable.Col()
    lat: float = doctable.Col()

    # use Col to use factory to construct emtpy list
    # will be stored as binary/pickle type, since no other available
    elements: Sequence = doctable.Col(list) 
    
    # indices and constraints
    _indices_ = {
        'lonlat_index': ('lon', 'lat', {'unique':True}),
        'name_index': ('name',),
    }
    _constraints_ = (
        ('check', 'lon > 0', {'name':'check_lon'}), 
        ('check', 'lat > 0'), 
        #('foreignkey', ('a','b'), ('c','d'))
    )

if __name__ == '__main__':
    mc = MyClass()
    for col in doctable.parse_schema_dataclass(MyClass):
        print(col)

    #for col in mc.sqlalchemy_columns():
    #    print(col)
    print(mc)
    print(mc.lon)
    try:
        print(mc['lon'])
    except Exception as e:
        print(e)

    db = doctable.DocTable(target=':memory:', schema=MyClass)
    db.insert(MyClass('hahhahha', elements='l o l ha ha ha'.split()))
    db.insert(MyClass('whatever'))
    print(db.head())
    print(db.schema_table())
    print(isinstance(mc, doctable.DocTableRow))
    for row in db.select(['idx', 'name']):
        print(f"{row.idx}: {row.name}")
    #print(fields(MyBaseClass))
    #mt = MyTable()
    #print(fields(mt.dclass))
    #print(fields(mc))
    #print(mc['name'])
    #print(mc)
    #print(mc.name)
    #print(fields(MyClass))
    #for f in fields(MyClass):
    #    f.default = 'WHATEVER'
    #print(fields(MyClass))


'''
Desired behavior:
# if column not in select statement
    raise exception that either (a) the object does not have this attr, or (b) 

default: Default value of the field
default_factory: Function that returns the initial value of the field
init: Use field in .__init__() method? (Default is True.)
repr: Use field in repr of the object? (Default is True.)
compare: Include the field in comparisons? (Default is True.)
hash: Include the field when calculating hash()? (Default is to use the same as for compare.)
metadata: A mapping with information about the field

'''