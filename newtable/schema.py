from __future__ import annotations

import typing
import dataclasses
import sqlalchemy

@dataclasses.dataclass
class ColumnInfo:
    dtype: sqlalchemy.TypeClause
    dtype_args: typing.Tuple[typing.Any, ...]
    dtype_kwargs: typing.Dict[str, typing.Any]
    column_kwargs: typing.Dict[str, typing.Any]

    @classmethod
    def from_field(cls, field: dataclasses.Field) -> ColumnInfo:
        '''Get column info from a dataclass field.'''
        pass
    
    def sqlalchemy_column(self, name: str) -> sqlalchemy.Column:
        column_type = self.dtype(*self.dtype_args, **self.dtype_kwargs)
        return sqlalchemy.Column(name, column_type, **self.column_kwargs)

@dataclasses.dataclass
class IndexInfo:
    column_names: typing.List[str]

    def sqlalchemy_index(self, name: str) -> sqlalchemy.Index:
        return sqlalchemy.Index(name, *self.column_names)

@dataclasses.dataclass
class Schema:
    '''Contains all information needed to construct a db table.'''
    table_name: str
    data_container: type
    columns: typing.Dict[str, ColumnInfo]
    indices: typing.Dict[str, IndexInfo]
    constraints: typing.List[sqlalchemy.Constraint]
    table_kwargs: typing.Dict[str, typing.Any]

    @classmethod
    def from_schema_decorator(cls, schema_class: type) -> Schema:
        pass

    def table_args(self) -> typing.List[typing.Union[sqlalchemy.Column, sqlalchemy.Index, sqlalchemy.Constraint]]:
        '''Get a list of all table args.'''
        return [*self.sqlalchemy_columns(), *self.sqlalchemy_indices(), *self.constraints]
    
    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        '''Get list of sqlalchemy columns.'''
        return [col.sqlalchemy_column(name) for name, col in self.columns.items()]

    def sqlalchemy_indices(self) -> typing.List[sqlalchemy.Index]:
        '''Get list of sqlalchemy indices.'''
        return [ind.sqlalchemy_index(name) for name, ind in self.indices.items()]

