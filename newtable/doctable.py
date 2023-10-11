

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

from .schema import TableSchema, get_schema, Container
    

@dataclasses.dataclass
class DocTable(DocTableBase, typing.Generic[Container]):
    schema: TableSchema[Container]
    table: sqlalchemy.Table
    core: ConnectCore

    @classmethod
    def from_container(cls, container_type: typing.Type[Container], core: ConnectCore) -> DocTable[Container]:
        '''Create a DocTable object from a data container class.'''
        return cls.from_schema(
            schema = get_schema(container_type),
            core=core,
        )

    @classmethod
    def from_schema(cls, schema: TableSchema[Container], core: ConnectCore) -> DocTable[Container]:
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
        return TableQuery.from_doctable(self)
    
    