from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import sqlalchemy.exc
import pandas as pd

from .dbtable import DBTable, ReflectedDBTable
from .query import ConnectQuery

if typing.TYPE_CHECKING:
    from .schema import TableSchema, Container

class TableAlreadyExistsError(Exception):
    pass

class TableDoesNotExistError(Exception):
    pass

            
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
        return DBTable.from_container(
            container_type=container_type,
            core=self.core,
            extend_existing=False,
            **kwargs,
        )

    def create_table_if_not_exists(self, *, container_type: typing.Type[Container], **kwargs) -> DBTable:
        '''Create a new table from a Schema class.
            Use extend_existing=True to connect to an existing table.
        '''
        return DBTable.from_container(
            container_type=container_type,
            core=self.core,
            extend_existing=True,
            **kwargs,
        )
    
    def reflect_table(self, table_name: str, **kwargs) -> DBTable:
        '''Create a new table from a Schema class.'''
        return ReflectedDBTable.from_existing_table(
            table_name=table_name,
            cc=self.core,
            **kwargs
        )

@dataclasses.dataclass
class ConnectCore:
    '''Manages an sqlalchemy engine and metadata object.'''
    target: str
    dialect: str
    engine: sqlalchemy.engine.Engine
    metadata: sqlalchemy.MetaData

    ################# Init #################
    @classmethod
    def open_new(cls, target: str, dialect: str, echo: bool = False, **engine_kwargs) -> ConnectCore:
        '''Connect to a new database (relevant only in sqlite, otherwise use open()).'''
        cls.check_target_exists(target, dialect, new_db=True)
        return cls.open(target=target, dialect=dialect, echo=echo, **engine_kwargs)
    
    @classmethod
    def open_existing(cls, target: str, dialect: str, echo: bool = False, **engine_kwargs) -> ConnectCore:
        '''Connect to an existing database (relevant only in sqlite, otherwise use open()).'''
        cls.check_target_exists(target, dialect, new_db=False)
        return cls.open(target=target, dialect=dialect, echo=echo, **engine_kwargs)
    
    @classmethod
    def open(cls, target: str, dialect: str, echo: bool = False, **engine_kwargs) -> ConnectCore:
        '''Connect to a database, creating it if it doesn't exist.'''
        engine, meta = cls.new_sqlalchemy_engine(target=target, dialect=dialect, echo=echo, **engine_kwargs)
        return cls(
            target=target,
            dialect=dialect,
            engine=engine,
            metadata=meta,
        )
        
    @staticmethod
    def check_target_exists(target: str, dialect: str, new_db: bool) -> bool:
        '''Raise exception if the target database does not exist.'''
        if dialect.startswith('sqlite') and target != ':memory:':
            if new_db and os.path.exists(target):
                raise FileExistsError(f'Database {target} already exists. Call connect_existing() instead.')
            elif not new_db and not os.path.exists(target):
                raise FileNotFoundError(f'Database {target} does not exist yet. Call connect_new() instead.')
        
    @staticmethod
    def new_sqlalchemy_engine(target: str, dialect: str, echo: bool = False, **engine_kwargs) -> typing.Tuple[sqlalchemy.engine.Engine, sqlalchemy.MetaData]:
        engine = sqlalchemy.create_engine(f'{dialect}:///{target}', echo=echo, **engine_kwargs)
        meta = sqlalchemy.MetaData()
        return engine, meta
    
    ################# Context Managers #################
    def emit_ddl(self) -> DDLEmitter:
        '''Context manager that creates tables on exit. Use for multi-table schemas.'''
        return DDLEmitter(self)
        
    def query(self) -> ConnectQuery:
        '''Create a connection and interface that can be used to make queries.'''
        return ConnectQuery(self.engine.connect())

    ################# Tables #################
    def get_dbtable(table_name: str) -> DBTable:
        pass

    ################# Queries #################
    def sqlalchemy_table(self, table_name: str, columns: list[sqlalchemy.Column], extend_existing: bool = False, **kwargs) -> sqlalchemy.Table:
        '''Create a new table in the database. Use extend_existing = True to use an existing table.'''
        # ideally the user will not enable extend_existing = True
        try:
            return sqlalchemy.Table(table_name, self.metadata, *columns, extend_existing=extend_existing, **kwargs)
        except sqlalchemy.exc.InvalidRequestError as e:
            m = str(e)
            # idk about this if statement, but copilot wrote it.
            if 'already exists' in m or 'already defined' in m:
                raise TableAlreadyExistsError(f'The table {table_name} already exists. '
                    'To reflect an existing table, use reflect_sqlalchemy_table(). '
                    'You may also use the extend_existing=True flag to optionally  '
                    'extend an exesting table.') from e
            else:
                raise e
    
    def reflect_sqlalchemy_table(self, table_name: str, **kwargs) -> sqlalchemy.Table:
        '''Reflect a table that already exists in the database.
            Note: if table already exists as part of the metadata, it will return that table instance.
        '''
        try:
            return sqlalchemy.Table(table_name, self.metadata, autoload_with=self.engine, **kwargs)
        except sqlalchemy.exc.NoSuchTableError as e:
            raise TableDoesNotExistError(f'The table {table_name} does not exist. '
                'To create a new table, use sqlalchemy_table().') from e
    
    ################# Connections #################

    ################# Engine interface #################
    def begin(self) -> sqlalchemy.engine.Transaction:
        ''' Open new transaction in the engine connection pool.
        https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html
        '''
        return self.engine.begin()
    
    def connect(self) -> sqlalchemy.engine.Connection:
        ''' Open new connection in the engine connection pool.
        https://docs.sqlalchemy.org/en/20/tutorial/dbapi_transactions.html
        '''
        return self.engine.connect()
    
    def list_tables(self) -> typing.List[str]:
        ''' List table names in database connection.
        '''
        return self.engine.table_names()
    
    def dispose_engine(self) -> sqlalchemy.engine.ResultProxy:
        ''' Closes all existing connections attached to engine.
        '''
        return self.engine.dispose()

    ################# Metadata interface #################
    @property
    def metadata_tables(self) -> typing.Dict[str, sqlalchemy.Table]:
        ''' Access metadata.tables
        '''
        return self.metadata.tables
    
    def metadata_reflect(self, **kwargs) -> None:
        ''' Will register all existing tables using metadata.reflect().
        '''
        #for tabname in self.list_tables():
        #    self.add_table(tabname, **kwargs)
        return self.metadata.reflect(**kwargs)
    
    def create_all_tables(self) -> None:
        ''' Create all tables in metadata.
        '''
        return self.metadata.create_all(self.engine)

    ################# Inspection methods #################
    def inspect_columns_all(self) -> typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]]:
        '''Get column info for all tables.'''
        inspector = self.inspector()
        return {tn:inspector.get_columns(tn) for tn in inspector.get_table_names()}
    
    def inspect_indices_all(self) -> typing.Dict[str, typing.List[typing.Dict[str, typing.Any]]]:
        '''Get index info for all tables.'''
        inspector = self.inspector()
        return {tn:inspector.get_indexes(tn) for tn in inspector.get_table_names()}

    def inspect_columns(self, table_name: str) -> typing.List[sqlalchemy.Column]:
        '''Get list of columns for a table.
        '''
        return self.inspector().get_columns(table_name)

    def inspect_indices(self, table_name: str) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Wraps Inspector.get_indexes(tabname).'''
        return self.inspector().get_indexes(table_name)
    
    def inspect_table_names(self) -> typing.List[str]:
        '''Wraps Inspector.get_indexes(tabname).'''
        return self.inspector().get_table_names()
    
    def inspector(self) -> sqlalchemy.engine.Inspector:
        '''Get engine for this inspector.
        https://docs.sqlalchemy.org/en/14/core/reflection.html#sqlalchemy.engine.reflection.Inspector
        '''
        return sqlalchemy.inspect(self.engine)

    ################# Low-level execution methods #################
    def enable_foreign_keys(self) -> sqlalchemy.engine.ResultProxy:
        return self.execute('pragma foreign_keys=ON')

    def execute(self, query:str, *args, **kwargs) -> sqlalchemy.engine.CursorResult:
        '''Execute query using a temporary connection.
        '''
        return self.engine.execute(query, *args, **kwargs)

