

from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd

from .doctablebase import DocTableBase

if typing.TYPE_CHECKING:
    from .connectcore import ConnectCore
    from .schema import Schema
    
@dataclasses.dataclass
class DocTable(DocTableBase):
    schema: Schema
    table: sqlalchemy.Table
    core: ConnectCore

    @classmethod
    def from_schema(cls, schema: Schema, core: ConnectCore, **kwargs) -> DocTable:
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
    
    