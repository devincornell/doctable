from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import functools

from ..column import ColumnInfo
from .index import IndexInfo, IndexParams
from ..missing import MISSING

from .general import set_schema, get_schema, Container

@dataclasses.dataclass
class AttrColNameMappings:
    '''Contains all information needed to construct a db table.'''
    attr_to_col: typing.Dict[str, str]
    col_to_attr: typing.Dict[str, str]
    empty_col_kwargs: typing.Dict[str, typing.Any]
    empty_attr_kwargs: typing.Dict[str, typing.Any]

    @classmethod
    def from_column_infos(cls, column_infos: typing.List[ColumnInfo]) -> AttrColNameMappings:
        pairs = [ci.name_translation() for ci in column_infos]
        attr_to_col = {attr: col for attr, col in pairs}
        col_to_attr = {col: attr for attr, col in pairs}
        return cls(
            attr_to_col = attr_to_col,
            col_to_attr = col_to_attr, 
            empty_col_kwargs = {k: MISSING for k in col_to_attr.keys()},
            empty_attr_kwargs = {k: MISSING for k in attr_to_col.keys()},
        )

@dataclasses.dataclass
class TableSchema(typing.Generic[Container]):
    '''Contains all information needed to construct and work with a db table.
    '''
    table_name: str
    container_type: typing.Type[Container]
    columns: typing.List[ColumnInfo]
    indices: typing.List[IndexInfo]
    constraints: typing.List[sqlalchemy.Constraint]
    table_kwargs: typing.Dict[str, typing.Any] # extra args meant to be passed when creating table
    name_mappings:AttrColNameMappings # attribute name to column mapping

    @classmethod
    def from_container(cls, 
        table_name: str, 
        container_type: typing.Type[Container],
        indices: typing.Dict[str, IndexParams],
        constraints: typing.List[sqlalchemy.Constraint],
        table_kwargs: typing.Dict[str, typing.Any],
    ) -> TableSchema[Container]:
        '''Create from basic args - called directly from decorator.'''
        column_infos = cls.parse_column_infos(container_type)
        #col_to_attr, attr_to_col = cls.get_column_mappings(column_infos)
        return cls(
            table_name=table_name,
            container_type=container_type,
            columns=column_infos,
            indices=[IndexInfo.from_params(name, params) for name, params in indices.items()],
            constraints=constraints,
            table_kwargs=table_kwargs,
            name_mappings = AttrColNameMappings.from_column_infos(column_infos),
        )
    
    @staticmethod
    def parse_column_infos(container_type: typing.Type[Container]) -> typing.List[ColumnInfo]:
        '''Get column infos from a container type.'''
        infos = [ColumnInfo.from_field(field, i) for i, field in enumerate(dataclasses.fields(container_type))]
        return list(sorted(infos, key=lambda ci: ci.order_key()))

    #################### Converting to/from Container Types ####################
    def container_from_row(self, row: sqlalchemy.Row) -> Container:
        '''Get a data container from a row.'''
        col_to_attr = self.name_mappings.col_to_attr
        kwargs = {
            **self.name_mappings.empty_attr_kwargs, 
            **{col_to_attr[k]:v for k,v in row._mapping.items()}
        }
        return self.container_type(**kwargs)
    
    def dict_from_container(self, container: Container) -> typing.Dict[str, typing.Any]:
        '''Get a dictionary representation of this schema for insertion, ignoring MISSING values.'''
        attr_to_col = self.name_mappings.attr_to_col
        try:
            # NOTE: this old implementation does recursive serialization
            #values = dataclasses.asdict(container).items()
            #return {attr_to_col[k]:v for k,v in values if v is not MISSING}
            
            # add type hint?  (Container is dataclasses.DataclassInstance)
            fields = dataclasses.fields(container)
            return {attr_to_col[f.name]:v for f in fields if (v := getattr(container, f.name)) is not MISSING}
            
        except TypeError as e:
            raise TypeError(f'"{container}" is not a recognized container. '
                'Use ConnectCore.insert if inserting raw dictionaries.') from e

    #################### Creating Tables ####################
    def sqlalchemy_table(self, metadata: sqlalchemy.MetaData, **kwargs) -> sqlalchemy.Table:
        '''Depricated. Creates and returns new sqlalchemy table..'''
        name, args, kwargs = self.sqlalchemy_table_args(**kwargs)
        return sqlalchemy.Table(name, metadata, *args, **kwargs)
    
    def sqlalchemy_table_args(self,**kwargs) -> typing.Tuple[str, typing.List, typing.Dict]:
        '''Get name, args, kwargs tuple for creating an sqlalchemy table.'''
        return (self.table_name, self.table_args(), {**self.table_kwargs, **kwargs})
    
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


