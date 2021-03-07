

import sqlalchemy as sa
import datetime
from dataclasses import dataclass, field, fields
from typing import Union, Mapping, Sequence, Tuple, Set, List





########################## Row Object Base Class ##########################
class RowBase:
    ''' Base class for column objects.
    '''
    miss_col_message = 'The column "{name}" was not retreived in the select statement.'

    ########################## Basic Accessors ##########################
    def __getitem__(self, attr):
        ''' Access data, throwing error when accessing element that was not
                retrieved from the database.
        '''
        val = self.__dict__[attr]
        if isinstance(val, EmptyValue):
            raise KeyError(self.miss_col_message.format(name=attr))
        return val
    
    @property
    def v(self):
        ''' Access data without throwing an error when accessing element.
        '''
        return self.__dict__
    
    def __repr__(self):
        cn = ", ".join([(f'{k}=\'{v}\'' if isinstance(v,str) else f'{k}={v}') 
                            for k,v in self.as_dict().items()])
        return f'{self.__class__.__name__}({cn})'
    
    ########################## Conversions ##########################
    def as_dict(self):
        ''' Convert to dictionary, ignoring EmptyValue objects.
        '''
        return {k:v for k,v in self.__dict__.items() if not isinstance(v, EmptyValue)}

########################## SQLAlchemy Converters ##########################
class SQLAlchemyConverter()
    type_lookup = {
        int: sa.Integer,
        float: sa.Float,
        str: sa.String,
        bool: sa.Boolean,
        datetime.datetime: sa.DateTime,
        datetime.time: sa.Time,
        datetime.date: sa.Date,
    }
    def __init__(self, row_obj, indices, constraints):
        self.row = row_obj
        self.indices = indices
        self.constraints = constraints
    
    def sqlalchemy_columns(self):
        columns = list()
        
        # regular data columns
        for f in fields(self.row):
            if f.init:
                use_type = self.type_lookup.get(f.type, sa.PickleType)
                col = sa.Column(f.name, use_type, **f.metadata)
                columns.append(col)

        # indices
        if self.indices is not None:
            for name, (cols, kwargs) in self.indices.items():
                columns.append(sa.Index(name, *cols, **kwargs))

        if self.constraints is not None:
            for ctype,  in constraints:

        return column

@dataclass(repr=False)
class MyClass(RowBase):
    name: str = Col(unique=True)
    lon: float = Col()
    lat: float = Col()
    elements: Sequence = Col(list) # use Col to use factory to construct emtpy list


if __name__ == '__main__':
    mc = MyClass('Sally')

    #for col in mc.sqlalchemy_columns():
    #    print(col)
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