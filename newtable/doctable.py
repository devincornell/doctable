

from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd

if typing.TYPE_CHECKING:
    from .connectcore import ConnectCore
    from .schema import Schema
    
@dataclasses.dataclass
class DocTable:
    schema: Schema
    table: sqlalchemy.Table
    core: ConnectCore

    @classmethod
    def from_schema(cls, schema: Schema, core: ConnectCore, **kwargs) -> DocTable:
        '''Create a DocTable object from a Schema object.'''
        return cls(
            schema = schema,
            table = core.new_sqlalchemy_table(
                table_name=schema.table_name, 
                columns=schema.table_args(), 
                **schema.table_kwargs,
                **kwargs
            ),
            cc=core,
        )
    
    @classmethod
    def connect_existing(cls, table: sqlalchemy.Table, engine: ConnectCore) -> DocTable:
        '''Create a DocTable object from an existing sqlalchemy table.'''
        return cls(
            table=table,
            engine=engine,
        )
    
    @classmethod
    def create_new(cls, schema: Schema, engine: ConnectCore) -> DocTable:
        '''Create a DocTable object from an existing sqlalchemy table.'''
        
        return cls(
            engine=engine,
        )
    
    @property
    def name(self) -> str:
        return self.table.name
    
    