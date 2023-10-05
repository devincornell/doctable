from __future__ import annotations

import dataclasses
import typing
import sqlalchemy

from .querybuilder import QueryBuilder

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
    def select_scalar(self, 
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
        
        row = self.select_first(
            cols = self.parse_input_col(col),
            where = where,
            orderby = orderby,
            groupby = groupby,
            wherestr = wherestr,
            offset = offset,
            raw_result = True,
            **kwargs
        )
        return row[0]


    def select_col(self, 
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
        
        q = QueryBuilder.select_query(
            cols = [col],
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        )
        result = self.execute(q, **kwargs)
        return [r[0] for r in result.all()]

    def select_first(self,
        cols: typing.List[sqlalchemy.Column],
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None,
        orderby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        groupby: typing.Optional[typing.List[sqlalchemy.Column]] = None,
        wherestr: typing.Optional[str] = None,
        offset: typing.Optional[int] = None,
        **kwargs
    ) -> sqlalchemy.engine.result.Row:
        
        q = QueryBuilder.select_query(
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
            raise LookupError('No results were returned. Needed to error '
                'so this result wasn not confused with case where actual '
                'result is None. If not sure about result, use regular '
                '.select() method with limit=1.')
        return result

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
        '''Most basic select method.        
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
            wherestr (str): raw sql "where" conditionals to add to where input
            **kwargs: passed to self.execute()
        '''
        q = QueryBuilder.select_query(
            cols = cols,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        )
        return self.execute_query(q, **kwargs).all()

    def execute_query(self, 
        query: typing.Union[sqlalchemy.sql.Insert, sqlalchemy.sql.Select, sqlalchemy.sql.Update, sqlalchemy.sql.Delete], 
        **kwargs
    ) -> sqlalchemy.engine.Result:
        '''Execute a query using a query builder object.'''
        return self.conn.execute(query, **kwargs)
    
    def execute(self, query_str: str, *args, **kwargs) -> sqlalchemy.engine.Result:
        '''Execute raw sql query.'''
        return self.conn.execute(sqlalchemy.text(query_str), *args, **kwargs)


