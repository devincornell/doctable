from __future__ import annotations

import typing
import dataclasses
import sqlalchemy

from .column import ColumnInfo

def index(*column_names: typing.List[str], **kwargs: typing.Dict[str, typing.Any]) -> IndexInfo:
    return IndexInfo(
        column_names=column_names,
        kwargs=kwargs,
    )

@dataclasses.dataclass
class IndexInfo:
    column_names: typing.List[str]
    kwargs: typing.Dict[str, typing.Any]

    def sqlalchemy_index(self, name: str) -> sqlalchemy.Index:
        return sqlalchemy.Index(name, *self.column_names, **self.kwargs)


T = typing.TypeVar('T')

@dataclasses.dataclass
class Schema(typing.Generic[T]):
    '''Contains all information needed to construct a db table.'''
    table_name: str
    container_type: typing.Type[T]
    indices: typing.Dict[str, IndexInfo]
    constraints: typing.List[sqlalchemy.Constraint]
    table_kwargs: typing.Dict[str, typing.Any]

    #################### Converting to/from Container Types ####################
    def container_from_row(self, row: sqlalchemy.Row) -> T:
        '''Get a data container from a row.'''
        return self.container_type(**row._mapping)
    
    def dict_from_container(self, container: T) -> typing.Dict[str, typing.Any]:
        '''Get a dictionary representation of this schema.'''
        return dataclasses.asdict(container)

    #################### Table Arguments ####################
    def table_args(self) -> typing.List[typing.Union[sqlalchemy.Column, sqlalchemy.Index, sqlalchemy.Constraint]]:
        '''Get a list of all table args.'''
        return [*self.sqlalchemy_columns(), *self.sqlalchemy_indices(), *self.constraints]

    def sqlalchemy_indices(self) -> typing.List[sqlalchemy.Index]:
        '''Get list of sqlalchemy indices.'''
        return [ind.sqlalchemy_index(name) for name, ind in self.indices.items()]

    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        '''Get column objects from .'''
        columns = list()
        for field in dataclasses.fields(self.container_type):
            columns.append(ColumnInfo.from_field(field))
        return columns


