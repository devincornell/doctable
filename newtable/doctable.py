

from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd

from .doctablebase import DocTableBase
from .query import TableQuery

if typing.TYPE_CHECKING:
    from .connectcore import ConnectCore
    from .schema import Schema
    

T = typing.TypeVar('T')

@dataclasses.dataclass
class DocTable(DocTableBase, typing.Generic[T]):
    schema: Schema[T]
    table: sqlalchemy.Table
    core: ConnectCore

    @classmethod
    def from_schema(cls, schema: Schema[T], core: ConnectCore, **kwargs) -> DocTable:
        '''Create a DocTable object from a Schema object.'''
        return cls(
            schema = schema,
            table = core.sqlalchemy_table(
                table_name=schema.table_name, 
                columns=schema.table_args(), 
                **schema.table_kwargs,
                **kwargs
            ),
            core=core,
        )
        
    @property
    def name(self) -> str:
        return self.table.name
    
    def query(self) -> TableQuery:
        '''Return a TableQuery object for querying this table.'''
        return TableQuery.from_doctable(self, self.core.query())
    
    