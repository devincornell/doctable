from __future__ import annotations

from ..sentinels import MISSING_VALUE
import dataclasses
import typing
import functools

#from ..sentinels import MISSING_VALUE
from .errors import RowDataNotAvailableError
from .operators import get_attr_map, attr_value, attr_value_tuples, asdict, asdict_ignore_missing

miss_col_message = 'The column "{name}" was not retreived in the select statement.'



@dataclasses.dataclass
class PropertyAccessor:
    '''Access properties of the schema object without raising error for missing data.'''
    schema_obj: DocTableSchema
    def __getitem__(self, pname: str):
        return attr_value(self.schema_obj, pname)

    def is_missing(self, pname: str):
        return attr_value(self.schema_obj, pname) is MISSING_VALUE

class DocTableSchema:
    ''' Base class for column objects.
    '''
    __slots__ = [] # for inheriting class

    ########################## Basic Accessors ##########################    
    def __getitem__(self, attr):
        ''' Access data, throwing error when accessing element that was not
                retrieved from the database.
        '''
        return getattr(self, attr)        
    
    @property
    def v(self) -> PropertyAccessor:
        '''Access properties of the schema object without raising exception 
            for missing data.
        '''
        return PropertyAccessor(self)
    
    def get_value(self, property_name: str):
        ''' Access data at a given value.
        '''
        return attr_value(self, property_name)
            
    def __repr__(self):
        '''Hides cols with values of type MISSING_VALUE.
        '''
        cn = ", ".join([(f'{pn}=\'{v}\'' if isinstance(v,str) else f'{pn}={v}') 
            for pn,an,v in attr_value_tuples(self)])
        return f'{self.__class__.__name__}({cn})'
    
    ########################## Conversions ##########################
    
    def asdict(self, *args, **kwargs):
        '''Convert object to dictionary, including missing value.
        '''
        return asdict(self, *args, **kwargs)
      
    def asdict_ignore_missing(self, *args, **kwargs):
        '''Convert object to dictionary, omitting missing value.
        '''
        return asdict_ignore_missing(self, *args, **kwargs)
