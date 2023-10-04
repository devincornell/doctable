

from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd

if typing.TYPE_CHECKING:
    from .connectengine import ConnectEngine
    
@dataclasses.dataclass
class DocTable:
    table: sqlalchemy.Table
    engine: ConnectEngine
    
    @classmethod
    def from_engine(cls, table_name: str, engine: ConnectEngine) -> DocTable:
        return cls(
            table=engine.get_table_metadata(table_name),
            engine=engine,
        )
    
    @property
    def name(self) -> str:
        return self.table.name
    
    