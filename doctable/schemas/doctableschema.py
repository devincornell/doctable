from __future__ import annotations

import dataclasses
import typing
import functools

from .missingvalue import MISSING_VALUE
from .errors import RowDataNotAvailableError

miss_col_message = 'The column "{name}" was not retreived in the select statement.'


def colname_to_property(colname: str) -> str:
    return f'_doctable__{colname}'

def property_to_colname(property: str) -> str:
    return '__'.join(property.split('__')[1:])


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
    
    def get_val(self, colname):
        ''' Access data related to the property.
        '''
        return self._doctable_get_val(colname)
        
    def _doctable_get_val(self, colname):
        '''Access column data without raising exception when accessing property.'''
        return getattr(self, self.__doctable_property_names__[colname])
    
    def __repr__(self):
        '''Hides cols with values of type MISSING_VALUE.
        '''
        cn = ", ".join([(f'{k}=\'{v}\'' if isinstance(v,str) else f'{k}={v}') 
            for k,v in self._doctable_as_dict().items()])
        return f'{self.__class__.__name__}({cn})'
    
    ########################## Conversions ##########################
    
    def as_dict(self, *args, **kwargs):
        '''Public interface for _doctable_as_dict().
        '''
        return self._doctable_as_dict(*args, **kwargs)

    def _doctable_as_dict(self):
        '''Convert to dictionary, ignoring MISSING_VALUE objects.
        '''
        try:
            return {f.name:getattr(self,f.name) for f in dataclasses.fields(self) 
                                        if self.get_val(f.name) is not MISSING_VALUE}
        except AttributeError:
            return {f.name:getattr(self,f.name) for f in dataclasses.fields(self) 
                                        if getattr(self,f.name) is not MISSING_VALUE}
      
    @classmethod
    def _doctable_from_db(cls, row: typing.Dict[str, typing.Any]):
        '''DocTable uses this as a constructor to fill missing values with MISSING_VALUE objects.
        '''
        row = dict(row)
        return cls(**{f.name:row.get(f.name,MISSING_VALUE) for f in dataclasses.fields(cls)})
    
    
