import dataclasses
import typing
import sqlalchemy

from .querybuilder import QueryBuilder

@dataclasses.dataclass
class ConnectQuery:
    con = typing.Union[sqlalchemy.engine.Connection, sqlalchemy.engine.Engine]

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
        
        return self.con.execute(q, **kwargs).all()




