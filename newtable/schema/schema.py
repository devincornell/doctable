from __future__ import annotations

import typing
import dataclasses
import sqlalchemy

from .column import ColumnInfo

@dataclasses.dataclass
class IndexInfo:
    column_names: typing.List[str]

    @classmethod
    def new(cls, *column_names) -> IndexInfo:
        '''Get index info from only a sqlalchemy type.'''
        return cls(column_names=list(column_names))

    @classmethod
    def from_field(cls, field: dataclasses.Field) -> IndexInfo:
        '''Get index info from a dataclass field.'''
        pass

    def sqlalchemy_index(self, name: str) -> sqlalchemy.Index:
        return sqlalchemy.Index(name, *self.column_names)
    

T = typing.TypeVar('T')

@dataclasses.dataclass
class Schema(typing.Generic[T]):
    '''Contains all information needed to construct a db table.'''
    table_name: str
    container_type: typing.Type[T]
    indices: typing.Dict[str, IndexInfo]
    constraints: typing.List[sqlalchemy.Constraint]
    table_kwargs: typing.Dict[str, typing.Any]

    def sqlalchemy_indices(self) -> typing.List[sqlalchemy.Index]:
        '''Get list of index info.'''
        return list(self.indices.values())

    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        '''Get column objects from .'''
        columns = list()
        for field in dataclasses.fields(self.container_type):
            columns.append(ColumnInfo.from_field(field))
        return columns

    def container_from_row(self, row: sqlalchemy.Row) -> T:
        '''Get a data container from a row.'''
        return self.container_type(**row._mapping)
    
    def dict_from_container(self, container: T) -> typing.Dict[str, typing.Any]:
        '''Get a dictionary representation of this schema.'''
        return dataclasses.asdict(container)

    def table_args(self) -> typing.List[typing.Union[sqlalchemy.Column, sqlalchemy.Index, sqlalchemy.Constraint]]:
        '''Get a list of all table args.'''
        return [*self.sqlalchemy_columns(), *self.sqlalchemy_indices(), *self.constraints]
    
    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        '''Get list of sqlalchemy columns.'''
        return [col.sqlalchemy_column(name) for name, col in self.columns.items()]

    def sqlalchemy_indices(self) -> typing.List[sqlalchemy.Index]:
        '''Get list of sqlalchemy indices.'''
        return [ind.sqlalchemy_index(name) for name, ind in self.indices.items()]

