

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
    from .schema import TableSchema
    

T = typing.TypeVar('T')

@dataclasses.dataclass
class DocTable(DocTableBase, typing.Generic[T]):
    schema: TableSchema[T]
    table: sqlalchemy.Table
    core: ConnectCore

    @classmethod
    def from_schema(cls, schema: TableSchema[T], core: ConnectCore, **kwargs) -> DocTable:
        '''Create a DocTable object from a Schema object.'''
        return cls(
            schema = schema,
            table = schema.sqlalchemy_table(core.metadata),
            core=core,
        )
        
    @property
    def name(self) -> str:
        return self.table.name
    
    def query(self) -> TableQuery:
        '''Return a TableQuery object for querying this table.'''
        return TableQuery.from_doctable(self, self.core.query())
    
    