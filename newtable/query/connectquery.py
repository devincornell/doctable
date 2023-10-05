from __future__ import annotations

import dataclasses
import typing
import sqlalchemy
import sqlalchemy.exc

from .statementbuilder import StatementBuilder
from ..doctable import DocTable

@dataclasses.dataclass
class ConnectQuery:
    '''Query interface that is not associated with a particular db table.'''
    conn: sqlalchemy.engine.Connection

    #################### Context Manager ####################
    def __enter__(self) -> ConnectQuery:
        return self
    
    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        '''Create all tables in metadata.'''
        self.commit()

    def commit(self) -> None:
        return self.conn.commit()

    #################### Select Queries ####################
    def select_chunks(self, 
        cols: typing.List[sqlalchemy.Column],
        chunksize: int = 100, 
        limit: int = None, 
        **kwargs,
    ) -> typing.Generator[typing.List[sqlalchemy.engine.result.Row]]:
        ''' Performs select while querying only a subset of the results at a time. 
            Use when results set will take too much memory.
        '''
        
        offset = 0
        while True:
            
            rows = self.select(cols, offset=offset, limit=chunksize, **kwargs)
            chunk = rows[:limit-offset] if limit is not None else rows
            
            yield chunk
            
            offset += len(rows)
            
            if (limit is not None and offset >= limit) or len(rows) == 0:
                break
    
    def select(self, 
        cols: typing.List[sqlalchemy.Column],
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None,
        orderby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        groupby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        limit: typing.Optional[int] = None,
        wherestr: typing.Optional[str] = None,
        offset: typing.Optional[int] = None,
        **kwargs
    ) -> typing.List[sqlalchemy.engine.result.Row]:
        '''Most general select method.
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
            wherestr (str): raw sql "where" conditionals to add to where input
            **kwargs: passed to self.execute()
        '''
        q = StatementBuilder.select_query(
            cols = cols,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        )
        return self.execute_query(q, **kwargs).all()


    def select_scalar_one(self, 
        col: sqlalchemy.Column,
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None,
        orderby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        groupby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        limit: typing.Optional[int] = None,
        wherestr: typing.Optional[str] = None,
        offset: typing.Optional[int] = None,
        **kwargs
    ) -> typing.List[typing.Any]:
        '''Select values of a single column. Raises exception if not exactly one row is found.'''
        
        q = StatementBuilder.select_query(
            cols = [col],
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        )
        return self.execute(q, **kwargs).scalar_one()

    def select_column(self, 
        col: sqlalchemy.Column,
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None,
        orderby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        groupby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        limit: typing.Optional[int] = None,
        wherestr: typing.Optional[str] = None,
        offset: typing.Optional[int] = None,
        **kwargs
    ) -> typing.List[typing.Any]:
        '''Select values of a single column.'''
        
        q = StatementBuilder.select_query(
            cols = [col],
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        )
        # note: if the user had selected multiple columns, only the last one 
        # would be returned by scalar
        # https://docs.sqlalchemy.org/en/20/core/connections.html#sqlalchemy.engine.Result.scalars
        return self.execute(q, **kwargs).scalars().all()

    def select_first(self,
        cols: typing.List[sqlalchemy.Column],
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None,
        orderby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        groupby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        wherestr: typing.Optional[str] = None,
        offset: typing.Optional[int] = None,
        **kwargs
    ) -> sqlalchemy.engine.result.Row:
        
        q = StatementBuilder.select_query(
            cols = cols,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = 1,
            wherestr = wherestr,
            offset = offset,
        )
        result = self.execute(q, **kwargs).first()
        if result is None:
            raise sqlalchemy.exc.NoResultFound('No results were returned. '
                'If not sure about result, use .select() with limit=1.')
        return result


    #################### Insert Queries ####################
    def insert_multi(self, 
        dtable: DocTable,
        data: typing.List[typing.Dict[str, typing.Any]], 
        ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        if not self.is_sequence(data):
            raise TypeError('insert_multi accepts a sequence of rows to insert.')
        q = StatementBuilder.insert_query(dtable.table, ifnotunique=ifnotunique)
        return self.execute(q, data, **kwargs)

    def insert_single(self, 
        dtable: DocTable,
        data: typing.Dict[str, typing.Any], 
        ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        ''' Insert a single element into the database.
            Note: there is a performance cost to this because I enforce 
            the single using .values instead of binding the data. To avoid 
            this cost, past a single-element list to insert_multi instead.
        '''
        q = StatementBuilder.insert_query(
            dtable.table, 
            ifnotunique=ifnotunique
        ).values(**data)
        return self.execute(q, **kwargs)

    #################### Insert Queries ####################
    def update_single(self, 
        dtable: DocTable,
        values: typing.Dict[typing.Union[str,sqlalchemy.Column], typing.Any], 
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None, 
        wherestr: typing.Optional[str] = None,
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        '''Update row(s) assigning the provided values.'''
        q = StatementBuilder.update_query(
            table = dtable.table,
            where = where,
            wherestr = wherestr,
            preserve_parameter_order = self.is_sequence(values),
        ).values(values)         
        return self.execute_query(q, **kwargs)

    def update_many(self, 
        dtable: DocTable,
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
        q = StatementBuilder.update_query(
            table = dtable.table,
            where = where,
            wherestr = wherestr,
            preserve_parameter_order = self.is_sequence(values),
        )
        return self.execute_query(q, values, **kwargs)

    #################### Delete Queries ####################
    def delete(self, 
        dtable: DocTable,
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None, 
        wherestr: typing.Optional[str] = None,
        all: bool = False,
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        '''Update row(s) assigning the provided values.'''
        if where is None and wherestr is None and not all:
            raise ValueError('Must provide where or wherestr or set all=True.')

        q = StatementBuilder.delete_query(
            table = dtable.table,
            where = where,
            wherestr = wherestr,
        )
        return self.execute_query(q, **kwargs)


    #################### Query Execution ####################
    def execute_query(self, 
        query: typing.Union[sqlalchemy.sql.Insert, sqlalchemy.sql.Select, sqlalchemy.sql.Update, sqlalchemy.sql.Delete], 
        **kwargs
    ) -> sqlalchemy.engine.CursorResult:
        '''Execute a query using a query builder object.'''
        return self.conn.execute(query, **kwargs)
    
    def execute(self, query_str: str, *args, **kwargs) -> sqlalchemy.engine.CursorResult:
        '''Execute raw sql query.'''
        return self.conn.execute(sqlalchemy.text(query_str), *args, **kwargs)

    @staticmethod
    def is_sequence(obj: typing.Any) -> bool:
        return isinstance(obj, list) or isinstance(obj,tuple)
