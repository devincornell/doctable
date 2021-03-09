from typing import Union, Mapping, Sequence, Tuple, Set, List
from dataclasses import dataclass#, field, fields

import sys
sys.path.append('..')
import doctable


@dataclass
class MyClass(doctable.RowBase):
    
    # builtin column types
    idx: int = doctable.IDCol()
    updated: datetime.datetime = doctable.UpdatedCol()
    added: datetime.datetime = doctable.AddedCol()

    # custom column types 
    name: str = doctable.Col(unique=True)
    lon: float = doctable.Col()
    lat: float = doctable.Col()

    # use Col to use factory to construct emtpy list
    # will be stored as binary/pickle type, since no other available
    elements: Sequence = doctable.Col(list) 
    
    # indices and constraints
    __indices__ = {
        'my_index': ('c1', 'c2', {'unique':True}),
        'other_index': ('c1',),
    }
    __constraints__ = (
        ('check', 'x > 3', {'name':'salary_check'}), 
        ('foreignkey', ('a','b'), ('c','d'))
    )

if __name__ == '__main__':
    mc = MyClass()
    converter = doctable.SQLAlchemyConverter(MyClass)
    for col in converter.get_sqlalchemy_columns():
        print(col)

    #for col in mc.sqlalchemy_columns():
    #    print(col)
    print(mc)
    print(mc.lon)
    try:
        print(mc['lon'])
    except Exception as e:
        print(e)
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