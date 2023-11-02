

from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import pandas as pd

from .dbtablebase import DBTableBase

if typing.TYPE_CHECKING:
    from ..connectcore import ConnectCore

from ..schema import TableSchema, get_schema, Container
    

@dataclasses.dataclass
class DBTable(DBTableBase, typing.Generic[Container]):
    schema: TableSchema[Container]

    ############################ Creating Tables ############################
    @classmethod
    def extend(cls, 
        container_type: typing.Type[Container], 
        core: ConnectCore, 
        **kwargs
    ) -> DBTable[Container]:
        '''Create new table.'''
        schema = get_schema(container_type)
        return cls.from_schema(schema, core, core.extend_sqlalchemy_table, **kwargs)
        
    @classmethod
    def create(cls, 
        container_type: typing.Type[Container], 
        core: ConnectCore, 
        **kwargs
    ) -> DBTable[Container]:
        '''Create new table.'''
        schema = get_schema(container_type)
        return cls.from_schema(schema, core, core.create_sqlalchemy_table, **kwargs)
        
    @classmethod
    def from_schema(cls, 
        schema: TableSchema[Container],
        core: ConnectCore, 
        make_table_func: typing.Callable[[...], sqlalchemy.Table] = None,
        **kwargs
    ) -> DBTable[Container]:
        '''Create a new table from just a schema.
            make_table_func is either core.create_sqlalchemy_table or core.extend_sqlalchemy_table
        '''
        name, args, table_kwargs = schema.sqlalchemy_table_args(**kwargs)
        return cls(
            schema = schema,
            table = make_table_func(name, *args, **table_kwargs),
            core=core,
        )
        
    