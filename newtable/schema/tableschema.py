from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import functools

from .column import ColumnInfo, ColumnParams
from .index import IndexInfo, IndexParams

from .general import set_schema, get_schema, Container

@dataclasses.dataclass
class TableSchema(typing.Generic[Container]):
    '''Contains all information needed to construct a db table.'''
    table_name: str
    container_type: typing.Type[Container]
    columns: typing.List[ColumnInfo]
    indices: typing.List[IndexInfo]
    constraints: typing.List[sqlalchemy.Constraint]
    table_kwargs: typing.Dict[str, typing.Any]

    @classmethod
    def from_container(cls, 
        table_name: str, 
        container_type: typing.Type[Container],
        indices: typing.Dict[str, IndexParams],
        constraints: typing.List[sqlalchemy.Constraint],
        table_kwargs: typing.Dict[str, typing.Any],
    ) -> TableSchema[Container]:
        '''Create from basic args - called directly from decorator.'''
        return cls(
            table_name=table_name,
            container_type=container_type,
            columns=[ColumnInfo.from_field(field) for field in dataclasses.fields(container_type)],
            indices=[IndexInfo.from_params(name, params) for name, params in indices.items()],
            constraints=constraints,
            table_kwargs=table_kwargs,
        )

    #################### Converting to/from Container Types ####################
    def container_from_row(self, row: sqlalchemy.Row) -> Container:
        '''Get a data container from a row.'''
        return self.container_type(**row._mapping)
    
    def dict_from_container(self, container: Container) -> typing.Dict[str, typing.Any]:
        '''Get a dictionary representation of this schema.'''
        return dataclasses.asdict(container)

    #################### Creating Tables ####################
    def sqlalchemy_table(self, metadata: sqlalchemy.MetaData) -> sqlalchemy.Table:
        '''Get a sqlalchemy table object.'''
        print(self.table_name, self.table_args(), self.table_kwargs)
        return sqlalchemy.Table(
            self.table_name,
            metadata,
            *self.table_args(),
            **self.table_kwargs,
        )
    
    def table_args(self) -> typing.List[typing.Union[sqlalchemy.Column, sqlalchemy.Index, sqlalchemy.Constraint]]:
        '''Get a list of table args.'''
        return self.sqlalchemy_columns() + self.sqlalchemy_indices() + list(self.constraints)

    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        return [ci.sqlalchemy_column() for ci in self.columns]

    def sqlalchemy_indices(self) -> typing.List[sqlalchemy.Index]:
        '''Get list of sqlalchemy indices.'''
        return [ii.sqlalchemy_index() for ii in self.indices]



