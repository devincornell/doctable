from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import functools

from .column import ColumnInfo, ColumnParams
from .index import IndexInfo, IndexParams

from .tableschema import TableSchema
from .general import set_schema, get_schema, Container

def table_schema(
    _Cls: typing.Type[Container] = None, 
    table_name: typing.Optional[str] = None,
    indices: typing.Optional[typing.Dict[str, IndexParams]] = None,
    constraints: typing.Optional[typing.List[sqlalchemy.Constraint]] = None,
    init: bool = True, # these are all dataclass arguments (superset from 3.12)
    repr: bool = True, # passed to dataclasses.dataclass()
    eq: bool = True, # passed to dataclasses.dataclass()
    order: bool = False, # passed to dataclasses.dataclass()
    unsafe_hash: bool = False, # passed to dataclasses.dataclass()
    frozen: bool = False, # passed to dataclasses.dataclass()
    match_args: typing.Optional[bool] = None, # passed to dataclasses.dataclass()
    kw_only: typing.Optional[bool] = None, # passed to dataclasses.dataclass()
    slots: typing.Optional[bool] = None, # passed to dataclasses.dataclass()
    weakref_slot: typing.Optional[bool] = None, # passed to dataclasses.dataclass()
    **table_kwargs: typing.Dict[str, typing.Any],
) -> typing.Type[Container]:
    '''A decorator to change a regular class into a schema object class.
    '''
    # handle case with no indices or constraints
    indices = indices if indices is not None else dict()
    constraints = constraints if constraints is not None else list()
    
    #if table_name is None and _Cls is not None:
    #    table_name = _Cls.__name__

    # in case the user needs to access the old version
    def table_schema_decorator(Cls: typing.Type[Container]):
        # creates constructor/other methods using dataclasses
        try:
            dataclass_decorator = dataclasses.dataclass(
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
        except TypeError as e:
            if 'unexpected keyword argument' in str(e):
                if any([
                    match_args is not None, 
                    kw_only is not None, 
                    slots is not None, 
                    weakref_slot is not None
                ]):
                    raise TypeError('match_args, kw_only, slots, and weakref_slot '
                        'are only supported in Python 3.10+')
                
                dataclass_decorator = dataclasses.dataclass(
                    init = init,
                    repr = repr,
                    eq = eq,
                    order = order,
                    unsafe_hash = unsafe_hash,
                    frozen = frozen,
                )
            else:
                raise e
        
        NewCls = dataclass_decorator(Cls)
        
        # NOTE: don't need this since we re-used the original class
        #wrap_decorator = functools.wraps(Cls)
        #NewCls = wrap_decorator(NewCls)
        
        # NOTE: not sure this is a good idea, but table name takes name of class by default
        schema = TableSchema.from_container(
            table_name  = table_name if table_name is not None else NewCls.__name__,
            container_type = NewCls,
            indices = indices,
            constraints = constraints,
            table_kwargs = table_kwargs,
        )
        set_schema(NewCls, schema)

        return NewCls
                    
    if _Cls is None:
        return table_schema_decorator
    else:
        return table_schema_decorator(_Cls)