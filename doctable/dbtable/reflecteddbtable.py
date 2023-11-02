
from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd
from .dbtablebase import DBTableBase

if typing.TYPE_CHECKING:
    from ..connectcore import ConnectCore

    
@dataclasses.dataclass
class ReflectedDBTable(DBTableBase):

    @classmethod
    def from_existing_table(cls, table_name: str, core: ConnectCore, **kwargs) -> ReflectedDBTable:
        '''Create a DBTable object from an existing table when we do not have a schema.'''
        return cls(
            table = core.reflect_sqlalchemy_table(table_name=table_name, **kwargs),
            core=core,
        )



