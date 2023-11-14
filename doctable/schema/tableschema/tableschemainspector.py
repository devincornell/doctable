
from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import functools
import pandas as pd

from .general import set_schema, get_schema, Container

from .tableschema import TableSchema

def inspect_schema(container: Container) -> TableSchemaInspector:
    return TableSchemaInspector.from_container(container)


@dataclasses.dataclass
class TableSchemaInspector:
    '''Used to generate user-readable information about a 
        table before it has been created.
    '''
    schema: TableSchema[Container]
    
    @classmethod
    def from_container(cls, container: Container) -> TableSchemaInspector:
        try:
            return cls(schema=get_schema(container))
        except AttributeError as e:
            raise ValueError(f'The provided container '
                f'{type(container)} is not a proper schema.')
    
    def table_name(self) -> str:
        '''Get the name of the table.'''
        return self.schema.table_name
    
    def index_info_df(self) -> pd.DataFrame:
        '''Get a dataframe of index information.'''
        return pd.DataFrame(self.index_info())
    
    def index_info(self) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Get a dataframe of column information.'''
        return [ii.info_dict() for ii in self.schema.indices]
    
    def column_info_df(self) -> pd.DataFrame:
        '''Get a dataframe of column information.'''
        return pd.DataFrame(self.column_info())
    
    def column_info(self) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Get a dataframe of column information.'''
        return [ci.info_dict() for ci in self.schema.columns]
    
    
    



