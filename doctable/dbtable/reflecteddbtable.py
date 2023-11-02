
from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd
from .dbtablebase import DBTableBase

if typing.TYPE_CHECKING:
    from .connectcore import ConnectCore
    from .schema import Schema
    
@dataclasses.dataclass
class ReflectedDBTable(DBTableBase):
    table: sqlalchemy.Table
    core: ConnectCore

    @classmethod
    def from_existing_table(cls, table_name: str, core: ConnectCore, **kwargs) -> ReflectedDBTable:
        '''Create a DBTable object from a Schema object.'''
        return cls(
            table = core.reflect_sqlalchemy_table(table_name=table_name, **kwargs),
            core=core,
        )



