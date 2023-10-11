from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import functools

from .column import ColumnInfo, ColumnParams
from .index import IndexInfo, IndexParams

SCHEMA_ATTRIBUTE_NAME = '_table_schema'

T = typing.TypeVar('T')

def table_schema(
        _Cls: typing.Type[T] = None, 
        table_name: typing.Optional[str] = None,
        indices: typing.Optional[typing.Dict[str, IndexParams]] = None,
        constraints: typing.Optional[typing.List[sqlalchemy.Constraint]] = None,
        init: bool = True, # these are all dataclass arguments (superset from 3.12)
        repr: bool = True, # passed to dataclasses.dataclass()
        eq: bool = True, # passed to dataclasses.dataclass()
        order: bool = False, # passed to dataclasses.dataclass()
        unsafe_hash: bool = False, # passed to dataclasses.dataclass()
        frozen: bool = False, # passed to dataclasses.dataclass()
        match_args: bool = True, # passed to dataclasses.dataclass()
        kw_only: bool = False, # passed to dataclasses.dataclass()
        slots: bool = False, # passed to dataclasses.dataclass()
        weakref_slot: bool = True, # passed to dataclasses.dataclass()
        **table_kwargs: typing.Dict[str, typing.Any],
    ) -> typing.Type[T]:
    '''A decorator to change a regular class into a schema object class.
    '''
    # handle case with no indices or constraints
    indices = indices if indices is not None else dict()
    constraints = constraints if constraints is not None else list()

    # in case the user needs to access the old version
    def table_schema_decorator(Cls: typing.Type[T]):
        # creates constructor/other methods using dataclasses
        Cls: typing.Type[T] = dataclasses.dataclass(
            _Cls = Cls,
            init = init,
            repr = repr,
            eq = eq,
            order = order,
            unsafe_hash = unsafe_hash,
            frozen = frozen,
            match_args = match_args,
            kw_only = kw_only,
            slots = slots,
            weakref_slot = weakref_slot,
        )
        setattr(Cls, SCHEMA_ATTRIBUTE_NAME, TableSchema.from_container(
            table_name  = table_name,
            container_type = Cls,
            indices = indices,
            constraints = constraints,
            table_kwargs = table_kwargs,
        ))

        return Cls
                    
    if _Cls is None:
        return table_schema_decorator
    else:
        return table_schema_decorator(_Cls)

@dataclasses.dataclass
class TableSchema(typing.Generic[T]):
    '''Contains all information needed to construct a db table.'''
    table_name: str
    container_type: typing.Type[T]
    columns: typing.List[ColumnInfo]
    indices: typing.List[IndexInfo]
    constraints: typing.List[sqlalchemy.Constraint]
    table_kwargs: typing.Dict[str, typing.Any]

    @classmethod
    def from_container(cls, 
        table_name: str, 
        container_type: typing.Type[T],
        indices: typing.Dict[str, IndexParams],
        constraints: typing.List[sqlalchemy.Constraint],
        table_kwargs: typing.Dict[str, typing.Any],
    ) -> TableSchema[T]:
        '''Get a dictionary representation of this schema.'''
        return cls(
            table_name=table_name,
            container_type=container_type,
            columns=[ColumnInfo.from_field(field) for field in dataclasses.fields(container_type)],
            indices=[IndexInfo.from_params(name, params) for name, params in indices.items()],
            constraints=constraints,
            table_kwargs=table_kwargs,
        )

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
        return [ii.sqlalchemy_index() for ii in self.indices]

    def sqlalchemy_columns(self) -> typing.List[sqlalchemy.Column]:
        return [ci.sqlalchemy_column() for ci in self.columns]


