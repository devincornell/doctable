from __future__ import annotations
import typing
import dataclasses
import os
import sqlalchemy
import sqlalchemy.exc

from .dbtable import DDLEmitter
from .query import ConnectQuery

class TableAlreadyExistsError(Exception):
    pass

class TableDoesNotExistError(Exception):
    pass



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
        '''Connect to a database, creating it if it doesn't exist (in the case of sqlite).'''
        engine, meta = cls.new_sqlalchemy_engine(target=target, dialect=dialect, echo=echo, **engine_kwargs)
        return cls(
            target=target,
            dialect=dialect,
            engine=engine,
            metadata=meta,
        )
        
    @staticmethod
    def check_target_exists(target: str, dialect: str, new_db: bool) -> None:
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
    def begin_ddl(self) -> DDLEmitter:
        '''Context manager that creates tables on exit. Use for multi-table schemas.'''
        return DDLEmitter(self)
        
    def query(self) -> ConnectQuery:
        '''Create a connection and interface that can be used to make queries.'''
        return ConnectQuery(self.engine.connect())

    ################# Tables #################
    # NOTE: TODO
    #def get_dbtable(table_name: str) -> DBTable:
    #    pass

    ################# Queries #################
    def create_sqlalchemy_table(self, table_name: str, columns: list[sqlalchemy.Column], **kwargs) -> sqlalchemy.Table:
        '''Create a new table in the database. Raises exception if the table already exists..'''
        return self._sqlalchemy_table(table_name, columns, extend_existing=False, **kwargs)
        #try:
        #    return sqlalchemy.Table(table_name, self.metadata, *columns, extend_existing=False, **kwargs)
        #except sqlalchemy.exc.InvalidRequestError as e:
        #    m = str(e)
        #    # idk about this if statement, but copilot wrote it.
        #    if 'already exists' in m or 'already defined' in m:
        #        raise TableAlreadyExistsError(f'The table {table_name} already exists. '
        #            'To reflect an existing table, use reflect_sqlalchemy_table(). '
        #            'You may also use the extend_existing=True flag to optionally  '
        #            'extend an exesting table.') from e
        #    else:
        #        raise e

    def extend_sqlalchemy_table(self, table_name: str, columns: list[sqlalchemy.Column], **kwargs) -> sqlalchemy.Table:
        '''Create a new table if one does not exist, otherwise will add any indices, 
            constraints, or tables that did not exist previously.
            NOTE: should I revise this to raise an error if the table does not exist already?
        '''
        #return sqlalchemy.Table(table_name, self.metadata, *columns, extend_existing=True, **kwargs)
        return self._sqlalchemy_table(table_name, columns, extend_existing=True, **kwargs)
    
    def reflect_sqlalchemy_table(self, table_name: str, **kwargs) -> sqlalchemy.Table:
        '''Reflect a table that already exists in the database.
            Note: if table already exists as part of the metadata, it will return that table instance.
        '''
        return self._sqlalchemy_table(table_name, [], autoload_with=self.engine, **kwargs)
        #try:
        #    return sqlalchemy.Table(table_name, self.metadata, autoload_with=self.engine, **kwargs)
        #except sqlalchemy.exc.NoSuchTableError as e:
        #    raise TableDoesNotExistError(f'The table {table_name} does not exist. '
        #        'To create a new table, use sqlalchemy_table().') from e
            
    def _sqlalchemy_table(self, table_name: str, table_args: list[sqlalchemy.Column], **kwargs) -> sqlalchemy.Table:
        '''Base method for creating a new sqlalchemy table and handling exceptions that may be raised.'''
        # ideally the user will not enable extend_existing = True
        try:
            return sqlalchemy.Table(table_name, self.metadata, *table_args, **kwargs)
        
        except sqlalchemy.exc.NoSuchTableError as nste:
            raise TableDoesNotExistError(f'The table {table_name} does not exist. '
                'To create a new table, use create_sqlalchemy_table().') from nste
        
        except sqlalchemy.exc.InvalidRequestError as ire:
            m = str(ire)
            # idk about this if statement, but copilot wrote it.
            if 'already exists' in m or 'already defined' in m:
                raise TableAlreadyExistsError(f'The table {table_name} already exists. '
                    'To reflect or extend an existing table, use reflect_sqlalchemy_table() '
                    'or extend_sqlalchemy_table().'
                ) from ire
            else:
                raise ire
    
    ################# Connections #################

    ################# Engine interface #################
    def begin(self):
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
        # TODO: is this wrong? mypy says it is wrong.
        return list(self.metadata.tables.keys())
    
    def dispose_engine(self):
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
        ''' Create all tables in metadata. Must be used when creating new tables!!
        '''
        return self.metadata.create_all(self.engine)

    ################# Inspection methods #################
    def inspect_columns_all(self) -> typing.Dict[str, typing.List[sqlalchemy.engine.interfaces.ReflectedColumn]]:
        '''Get column info for all tables.'''
        inspector = self.inspector()
        return {tn:inspector.get_columns(tn) for tn in inspector.get_table_names()}
    
    def inspect_indices_all(self) -> typing.Dict[str, typing.List[sqlalchemy.engine.interfaces.ReflectedIndex]]:
        '''Get index info for all tables.'''
        inspector = self.inspector()
        return {tn:inspector.get_indexes(tn) for tn in inspector.get_table_names()}

    def inspect_columns(self, table_name: str) -> typing.List[sqlalchemy.engine.interfaces.ReflectedColumn]:
        '''Get list of columns for a table.
        '''
        return self.inspector().get_columns(table_name)

    def inspect_indices(self, table_name: str) -> typing.List[sqlalchemy.engine.interfaces.ReflectedIndex]:
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

    def execute(self, query: str, *args, **kwargs) -> sqlalchemy.engine.CursorResult:
        '''Execute query using a temporary connection.
        '''
        with self.engine.begin() as conn:
            return conn.execute(sqlalchemy.text(query), *args, **kwargs)

