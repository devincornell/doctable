
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
    table: sqlalchemy.Table
    engine: ConnectCore




