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
    table_kwargs: typing.Dict[str, typing.Any] # extra args meant to be passed when creating table
    attr_to_col: typing.Dict[str, str] # attribute name to column mapping
    col_to_attr: typing.Dict[str, str] # column name to attribute mapping
    auto_populate_cols: typing.Set[str] # columns that should be auto-populated

    @classmethod
    def from_container(cls, 
        table_name: str, 
        container_type: typing.Type[Container],
        indices: typing.Dict[str, IndexParams],
        constraints: typing.List[sqlalchemy.Constraint],
        table_kwargs: typing.Dict[str, typing.Any],
    ) -> TableSchema[Container]:
        '''Create from basic args - called directly from decorator.'''
        column_infos = [ColumnInfo.from_field(field) for field in dataclasses.fields(container_type)]
        col_to_attr, attr_to_col = cls.get_column_mappings(column_infos)
        return cls(
            table_name=table_name,
            container_type=container_type,
            columns=column_infos,
            indices=[IndexInfo.from_params(name, params) for name, params in indices.items()],
            constraints=constraints,
            table_kwargs=table_kwargs,
            attr_to_col=attr_to_col,
            col_to_attr=col_to_attr,
        )

    #################### Converting to/from Container Types ####################
    def container_from_row(self, row: sqlalchemy.Row) -> Container:
        '''Get a data container from a row.'''
        return self.container_type(**row._mapping)
    
    def dict_from_container(self, container: Container) -> typing.Dict[str, typing.Any]:
        '''Get a dictionary representation of this schema.'''
        try:
            return dataclasses.asdict(container)
        except TypeError as e:
            raise TypeError(f'"{container}" is not a recognized container. '
                'Use ConnectCore.insert if inserting raw dictionaries.') from e

    #################### Creating Tables ####################
    def sqlalchemy_table(self, metadata: sqlalchemy.MetaData, **kwargs) -> sqlalchemy.Table:
        '''Get a sqlalchemy table object.'''
        return sqlalchemy.Table(
            self.table_name,
            metadata,
            *self.table_args(),
            **self.table_kwargs,
            **kwargs,
        )
    
    def table_args(self) -> typing.List[typing.Union[sqlalchemy.Column, sqlalchemy.Index, sqlalchemy.Constraint]]:
        '''Get a list of table args.'''
        return self.sqlalchemy_columns() + self.sqlalchemy_indices() + list(self.constraints)

    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        return [ci.sqlalchemy_column() for ci in self.columns]

    def sqlalchemy_indices(self) -> typing.List[sqlalchemy.Index]:
        '''Get list of sqlalchemy indices.'''
        return [ii.sqlalchemy_index() for ii in self.indices]

    #################### Column Name Mappings ####################
    @staticmethod
    def get_column_mappings(column_infos: typing.List[ColumnInfo]) -> typing.Tuple[typing.Dict[str, str], typing.Dict[str, str], typing.Set[str]]:
        '''Get (column to attribute) and (attribute to column) name mappings, and auto-populated columns.'''
        col_to_attr = dict()
        attr_to_col = dict()
        for ci in column_infos:
            attr, col = ci.name_translation()
            col_to_attr[col] = attr
            attr_to_col[attr] = col
        return col_to_attr, attr_to_col


