

import sqlalchemy as sa
import datetime
from dataclasses import dataclass, field, fields
from typing import Union, Mapping, Sequence, Tuple, Set, List

class EmptyValue:
    pass

def Col(default=EmptyValue(), **colargs):
    if callable(default):
        default_arg = {'default_factory': default}
    else:
        default_arg = {'default': default}
    return field(init=True, metadata=colargs, repr=True, **default_arg)

class RowBase:
    miss_col_message = 'The column "{name}" was not retreived in the select statement.'
    type_lookup = {
        int: sa.Integer,
        float: sa.Float,
        str: sa.String,
        bool: sa.Boolean,
        datetime.datetime: sa.DateTime,
        datetime.time: sa.Time,
        datetime.date: sa.Date,
    }
    def __getitem__(self, attr):
        val = self.__dict__[attr]
        if isinstance(val, EmptyValue):
            raise KeyError(self.miss_col_message.format(name=attr))
        return val

    def __getattribute__(self, name):
        val = object.__getattribute__(self, name)
        if isinstance(val, EmptyValue):
            raise KeyError(self.miss_col_message.format(name=name))
        return val

    def coldata(self, cols):
        ''' Get data only for columns with present data.
        '''
        coldat = dict()
        for f in fields(self):
            try:
                coldat[f.name] = 
            

    def sqlalchemy_columns(self):
        columns = list()
        for f in fields(self):
            if f.init:
                use_type = self.type_lookup.get(f.type, sa.PickleType)
                columns.append(dict(name=f.name, type=use_type))
        return columns

@dataclass
class MyClass(RowBase):
    name: str = Col(part='first')
    lon: float = 0.5
    lat: float = None
    duh: Sequence = Col(default=list)

if __name__ == '__main__':
    mc = MyClass('test')

    print(mc.sqlalchemy_columns())
    print(mc)
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