from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..doctable import DocTable


import sqlalchemy
import dataclasses
import typing
import pandas as pd



from ..schema import DocTableSchema
from ..util import is_sequence

from .selectqueryargs import SelectQueryArgs
from .errors import *
from .selectquery import SelectQuery
from .deletequery import DeleteQuery
from .updatequery import UpdateQuery
from .insertquery import InsertQuery


@dataclasses.dataclass
class Query(SelectQuery, InsertQuery, UpdateQuery, DeleteQuery):
    dtab: DocTable
    
    ############################## General Purpose ##############################






