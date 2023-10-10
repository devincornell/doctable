from __future__ import annotations

import typing
import dataclasses
import sqlalchemy

from .column import ColumnInfo, ColumnParams
from .index import IndexInfo, IndexParams

def schema(
        _Cls: type = None, 
        **table_kwargs: typing.Dict[str, typing.Any]
    ) -> type:
    '''A decorator to change a regular class into a schema object class.
    '''
    # in case the user needs to access the old version
    if enable_properties:
        decorator_schema = schema_decorator_properties_factory(
            require_slots=require_slots, 
            dataclass_kwargs=dataclass_kwargs
        )
    else:
        decorator_schema = schema_decorator_basic_factory(
            require_slots=require_slots, 
            dataclass_kwargs=dataclass_kwargs
        )

    if _Cls is None:
        return decorator_schema
    else:
        return decorator_schema(_Cls)

def schema_decorator_properties_factory(
        require_slots: bool, 
        dataclass_kwargs: typing.Dict[str, typing.Any]
    ) -> typing.Callable[[type], type]:

    # this is the actual decorator
    def schema_decorator_with_properties(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')
        
        attr_map = dict()
        for field in dataclasses.fields(Cls):
            attr_name = property_to_attr(field.name)#f'_{field.name}'            
            attr_map[field.name] = attr_name
            
            # dataclasses don't actually create the property unless the default
            # value was a constant, so we just want to replicate that behavior
            # with MISSING_VALUE as the object. Normally it would do that in the 
            # constructor, but we want to create it ahead of time.
            if hasattr(Cls, field.name):
                setattr(Cls, attr_name, getattr(Cls, field.name))
            else:
                setattr(Cls, attr_name, MISSING_VALUE)
            
            # used a function to generate a class and return the property
            # to solve issue with class definitions in loops
            setattr(Cls, field.name, get_getter_setter(attr_name))
        
        # set map from properties to attributes
        set_attr_map(Cls, attr_map)
                
        # implement new hash function if needed
        if hasattr(Cls, '__hash__'):
            def hashfunc(self):
                return hash(as_value_tuple(self))
            Cls.__hash__ = hashfunc
            
        def binary_compare_factory(attrname: str):
            def binary_compare(self: Cls, other: Cls):
                return getattr(as_value_tuple(self), attrname)(as_value_tuple(other))
        
        if hasattr(Cls, '__eq__'): Cls.__eq__ = binary_compare_factory('__eq__')
        if hasattr(Cls, '__lt__'): Cls.__lt__ = binary_compare_factory('__lt__')
        if hasattr(Cls, '__le__'): Cls.__le__ = binary_compare_factory('__le__')
        if hasattr(Cls, '__gt__'): Cls.__gt__ = binary_compare_factory('__gt__')
        if hasattr(Cls, '__ge__'): Cls.__ge__ = binary_compare_factory('__ge__')
        
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = tuple(an for pn,an,v in attr_value_tuples(Cls))
            
        return NewClass
    
    return schema_decorator_with_properties


T = typing.TypeVar('T')

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


