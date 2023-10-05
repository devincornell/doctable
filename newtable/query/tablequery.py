import dataclasses
import typing
import sqlalchemy

from .connectquery import ConnectQuery

@dataclasses.dataclass
class TableQuery:
    table: sqlalchemy.Table
    cquery = ConnectQuery

    def from_(self, table: sqlalchemy.Table) -> ConnectQuery:
        '''Sets the table to query from.
        Args:
            table (sqlalchemy.Table): table to query from
        '''
        self.table = table
        return self

