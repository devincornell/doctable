from __future__ import annotations
import typing
import dataclasses

if typing.TYPE_CHECKING:
    from ..connectcore import ConnectCore
    from ..schema import Container

from .dbtable import DBTable
from .reflecteddbtable import ReflectedDBTable
            
@dataclasses.dataclass
class DDLEmitter:
    '''Interface for creating tables.'''
    core: ConnectCore
    
    def __enter__(self) -> DDLEmitter:
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        '''Create all tables in metadata.'''
        self.core.create_all_tables()
        
    def create_table(self, container_type: typing.Type[Container], **kwargs) -> DBTable:
        '''Create a new table from a Schema class.
        '''
        return DBTable.create(
            container_type=container_type,
            core=self.core,
            **kwargs,
        )

    def create_table_if_not_exists(self, container_type: typing.Type[Container], **kwargs) -> DBTable:
        '''Create a new table from a Schema class.
            Use extend_existing=True to connect to an existing table.
        '''
        return DBTable.extend(
            container_type=container_type,
            core=self.core,
            **kwargs,
        )
    
    def reflect_table(self, table_name: str, **kwargs) -> ReflectedDBTable:
        '''Create a new table from a Schema class.'''
        return ReflectedDBTable.from_existing_table(
            table_name=table_name,
            cc=self.core,
            **kwargs
        )
        
        