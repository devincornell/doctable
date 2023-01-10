from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..doctable import DocTable

import sqlalchemy
from .errors import SetToReadOnlyMode

SingleColumn = typing.Union[str, sqlalchemy.Column]
ColumnList = typing.List[SingleColumn]


class QueryBase:
    dtab: DocTable

    def _check_readonly(self, funcname: str) -> None:
        if self.dtab.readonly:
            raise SetToReadOnlyMode(f'Cannot {funcname} when doctable set to readonly.')


