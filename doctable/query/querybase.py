from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..doctable import DocTable

import sqlalchemy
from .errors import SetToReadOnlyMode

class QueryBase:
    dtab: DocTable



