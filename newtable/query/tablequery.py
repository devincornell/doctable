import dataclasses
import typing
import sqlalchemy

from .connectquery import ConnectQuery
from ..doctable import DocTable

@dataclasses.dataclass
class TableQuery:
    dtable: DocTable
    cquery: ConnectQuery

    @classmethod
    def from_sqlalchemy(cls, table: sqlalchemy.Table, cquery: ConnectQuery) -> ConnectQuery:
        '''Interface for quering tables.
        Args:
            table (sqlalchemy.Table): table to query from
        '''
        return cls(
            table=table,
            cquery=cquery,
        )
    
    def select(self, 
        cols: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None,
        order_by: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        group_by: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        limit: typing.Optional[int] = None,
        wherestr: typing.Optional[str] = None,
        offset: typing.Optional[int] = None,
        **kwargs
    ) -> ConnectQuery:
        '''Select from table.'''
        result = self.cquery.select(
            cols=cols if cols is not None else self.dtable.all_cols(),
            where=where,
            order_by=order_by,
            group_by=group_by,
            limit=limit,
            wherestr=wherestr,
            offset=offset,
            **kwargs
        )
        return [self.dtable.schema._from_row(**row) for row in result.all()]
    
    def insert_multi(self, 
        data: typing.List[typing.Dict[str, typing.Any]], 
        ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        return self.cquery.insert_multi(
            dtable=self.dtable,
            data=data,
            ifnotunique=ifnotunique,
            **kwargs
        )

    def insert_single(self, 
        data: typing.Dict[str, typing.Any], 
        ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        ''' Insert a single element into the database using the .values() clause.
            Note: there is a performance cost to this because I enforce 
            the single using .values instead of binding the data. To avoid 
            this cost, past a single-element list to insert_multi instead.
        '''
        return self.cquery.insert_single(
            dtable=self.dtable,
            data=data,
            ifnotunique=ifnotunique,
            **kwargs
        )
    #################### Insert Queries ####################
    def update_single(self, 
        values: typing.Dict[typing.Union[str,sqlalchemy.Column], typing.Any], 
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None, 
        wherestr: typing.Optional[str] = None,
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        '''Update row(s) using the .values() clause.'''
        return self.cquery.update_single(
            dtable=self.dtable,
            values=values,
            where=where,
            wherestr=wherestr,
            **kwargs
        )

    def update_many(self, 
        values: typing.List[typing.Dict[typing.Union[str,sqlalchemy.Column], typing.Any]], 
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None, 
        wherestr: typing.Optional[str] = None,
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        '''Update multiple rows in executemany parameter binding with bindparam().
            https://docs.sqlalchemy.org/en/20/tutorial/data_update.html
            
            NOTE: you MUST use bindparam for this to work. See sqlalchemy example below.
            >>> from sqlalchemy import bindparam
            >>> stmt = (
            ...     update(user_table)
            ...     .where(user_table.c.name == bindparam("oldname"))
            ...     .values(name=bindparam("newname"))
            ... )
            >>> with engine.begin() as conn:
            ...     conn.execute(
            ...         stmt,
            ...         [
            ...             {"oldname": "jack", "newname": "ed"},
            ...             {"oldname": "wendy", "newname": "mary"},
            ...             {"oldname": "jim", "newname": "jake"},
            ...         ],
            ...     )
        '''
        return self.cquery.update_many(
            dtable=self.dtable,
            values=values,
            where=where,
            wherestr=wherestr,
            **kwargs
        )

    #################### Delete Queries ####################
    def delete(self, 
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None, 
        wherestr: typing.Optional[str] = None,
        all: bool = False,
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        '''Update row(s) assigning the provided values.'''

        return self.cquery.delete(
            dtable=self.dtable,
            where=where,
            wherestr=wherestr,
            all=all,
            **kwargs
        )
