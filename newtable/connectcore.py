from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import sqlalchemy.exc
import pandas as pd
from .doctable import DocTable

class TableAlreadyExistsError(Exception):
    pass

class TableDoesNotExistError(Exception):
    pass

@dataclasses.dataclass
class ConnectCoreCreateTables:
    core: ConnectCore
    
    def __enter__(self) -> ConnectCoreCreateTables:
        return self.core
    
    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        '''Create all tables in metadata.'''
        self.core.create_all_tables()
        

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
        meta = sqlalchemy.MetaData(bind=engine)
        return engine, meta
    
    ################# Context Managers #################
    def create_tables(self) -> DocTable:
        '''For creating multiple tables at once.'''
        return ConnectCoreCreateTables(self)
        
    ################# Tables #################
    def get_doctable(table_name: str) -> DocTable:
        pass

    ################# Queries #################
    def new_sqlalchemy_table(self, table_name: str, columns: list[sqlalchemy.Column], **kwargs) -> sqlalchemy.Table:
        '''Create a new table in the database.'''
        # ideally the user will not enable extend_existing = True
        try:
            return sqlalchemy.Table(table_name, self.metadata, *columns, **kwargs)
        except sqlalchemy.exc.InvalidRequestError as e:
            m = str(e)
            if 'already exists' in m or 'already defined' in m: # idk about this if statement, but copilot wrote it.
                raise TableAlreadyExistsError(f'The table {table_name} already exists. '
                    'To reflect an existing table, use reflect_sqlalchemy_table(). '
                    'You may also use the extend_existing=True flag, but it is not '
                    'recommended.') from e
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
                'To create a new table, use new_sqlalchemy_table().') from e
    
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

    def inspect_indices(self, tabname: str) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Wraps Inspector.get_indexes(tabname).'''
        return self.inspector().get_indexes(tabname)
    
    def inspector(self) -> sqlalchemy.engine.Inspector:
        '''Get engine for this inspector.
        https://docs.sqlalchemy.org/en/14/core/reflection.html#sqlalchemy.engine.reflection.Inspector
        '''
        return sqlalchemy.inspect(self.engine)

    ################# Low-level execution methods #################
    def enable_foreign_keys(self) -> sqlalchemy.engine.ResultProxy:
        return self.execute('pragma foreign_keys=ON')

    def execute(self, query:str, *args, **kwargs) -> sqlalchemy.engine.ResultProxy:
        '''Execute query using a temporary connection.
        '''
        return self.engine.execute(query, *args, **kwargs)

