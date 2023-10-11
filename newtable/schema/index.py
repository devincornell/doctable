from __future__ import annotations

import typing
import dataclasses
import sqlalchemy

from .column import ColumnInfo

def Index(*column_names: typing.List[str], **kwargs: typing.Dict[str, typing.Any]) -> IndexInfo:
    return IndexParams(
        column_names=column_names,
        kwargs=kwargs,
    )

@dataclasses.dataclass
class IndexParams:
    '''Information passed by user.'''
    column_names: typing.List[str]
    kwargs: typing.Dict[str, typing.Any]
    
    def sqlalchemy_index(self, name: str) -> sqlalchemy.Index:
        return sqlalchemy.Index(name, *self.column_names, **self.kwargs)

@dataclasses.dataclass
class IndexInfo:
    '''Includes params and the name of the index needed to create the index.'''
    name: str
    params: IndexParams
    
    @classmethod
    def from_params(cls, name: str, params: IndexParams) -> IndexInfo:
        return cls(
            name=name,
            params=params,
        )

    def sqlalchemy_index(self) -> sqlalchemy.Index:
        return self.params.sqlalchemy_index(self.name)
