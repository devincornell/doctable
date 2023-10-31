
import typing
import dataclasses
from typing import Any

#if typing.TYPE_CHECKING:
import sqlalchemy


class DocTableBase:
    '''Contains interface for working with table wrappers.'''
    table: sqlalchemy.Table

    @property
    def table_name(self) -> str:
        return self.table.name

    def cols(self, *columns) -> typing.List[sqlalchemy.Column]:
        '''Return a query with only the specified columns.'''
        return [self.table.c[col] if isinstance(col, str) else col for col in columns]
    
    def all_cols(self) -> typing.List[sqlalchemy.Column]:
        return [c for c in self.table.columns]
    
    def __getitem__(self, key: Any) -> sqlalchemy.Column:
        '''Get a column by name.'''
        return self.table.c[key]
    
    def inspect_indices(self) -> typing.List[typing.Dict[str, typing.Any]]:
        '''Wraps Inspector.get_indexes(tabname).'''
        return self.inspector().get_indexes()

    def inspector(self) -> sqlalchemy.engine.Inspector:
        '''Get engine for this inspector.
        https://docs.sqlalchemy.org/en/14/core/reflection.html#sqlalchemy.engine.reflection.Inspector
        '''
        return sqlalchemy.inspect(self.table)
    

