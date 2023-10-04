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
class ConnectEngine:
    '''Manages an sqlalchemy engine and metadata object.'''
    target: str
    dialect: str
    engine: sqlalchemy.engine.Engine
    metadata: sqlalchemy.MetaData

    ################# Init #################

    @classmethod
    def new(cls, target: str, dialect: str = 'sqlite', new_db: bool = False, echo: bool = False, **engine_kwargs) -> ConnectEngine:
        if dialect.startswith('sqlite'):
            if target != ':memory:': #not creating in-memory database
                exists = os.path.exists(target)
                if not new_db and not exists:
                    raise FileNotFoundError('new_db is set to False but the database {} does not '
                                     'exist yet.'.format(target))

        engine, meta = cls.new_sqlalchemy_engine(target=target, dialect=dialect, echo=echo, **engine_kwargs)
        
        return cls(
            target=target,
            dialect=dialect,
            engine=engine,
            metadata=meta,
        )
        
    @staticmethod
    def new_sqlalchemy_engine(target: str, dialect: str, echo: bool = False, **engine_kwargs) -> typing.Tuple[sqlalchemy.engine.Engine, sqlalchemy.MetaData]:
        engine = sqlalchemy.create_engine(f'{dialect}:///{target}', echo=echo, **engine_kwargs)
        meta = sqlalchemy.MetaData(bind=engine)
        return engine, meta
    
    def enable_foreign_keys(self) -> sqlalchemy.engine.ResultProxy:
        return self.execute('pragma foreign_keys=ON')
    
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
                    'To reflect an existing table, use reflect_existing_table(). '
                    'You may also use the extend_existing=True flag, but it is not '
                    'recommended.') from e
            else:
                raise e
    
    def reflect_existing_table(self, table_name: str, **kwargs) -> sqlalchemy.Table:
        '''Reflect a table that already exists in the database.'''
        try:
            return sqlalchemy.Table(table_name, self.metadata, autoload_with=self.engine, **kwargs)
        except sqlalchemy.exc.NoSuchTableError as e:
            raise TableDoesNotExistError(f'The table {table_name} does not exist. '
                'To create a new table, use new_sqlalchemy_table().') from e
    
    def drop_table(self, table_name: str, if_exists: bool = False, **kwargs) -> None:
        '''Drops table, either sqlalchemy object or by executing DROP TABLE.
        Args:
            table (sqlalchemy.Table/str): table object or name to drop.
            if_exists (bool): if true, won't throw exception if table doesn't exist.
        '''
        pass

    ################# Connections #################
    def connect(self) -> sqlalchemy.engine.Connection:
        ''' Open new connection in the engine connection pool.
        '''
        return self.engine.connect()

    ################# Engine interface #################
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

    def execute(self, query:str, *args, **kwargs) -> sqlalchemy.engine.ResultProxy:
        '''Execute query using a temporary connection.
        '''
        return self.engine.execute(query, *args, **kwargs)

