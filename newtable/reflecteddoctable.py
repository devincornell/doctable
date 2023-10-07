
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
class ReflectedDocTable:
    table: sqlalchemy.Table
    engine: ConnectCore

    @classmethod
    def from_existing_table(cls, table_name: str, core: ConnectCore, **kwargs) -> ReflectedDocTable:
        '''Create a DocTable object from a Schema object.'''
        return cls(
            table = core.reflect_sqlalchemy_table(table_name=table_name, **kwargs),
            engine=core,
        )



