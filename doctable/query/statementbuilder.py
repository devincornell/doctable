
import sqlalchemy
import typing

class StatementBuilder:
    '''Methods for creating queries from sqlalchemy expressions.'''
    
    @staticmethod
    def select_query(
        cols: typing.List[sqlalchemy.Column],
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression],
        order_by: typing.Optional[typing.List[sqlalchemy.Column]],
        group_by: typing.Optional[typing.List[sqlalchemy.Column]],
        limit: typing.Optional[int],
        wherestr: typing.Optional[str],
        offset: typing.Optional[int],
    ) -> sqlalchemy.sql.Select:
        '''Build and exectute select query given all the conditionals provided as parameters.'''
        
        try:
            q: sqlalchemy.sql.Select = sqlalchemy.sql.select(*cols)
        except NotImplementedError as e:
            raise NotImplementedError(f'Did you mean to pass a list of columns to select?') from e
        
        if where is not None:
            q = q.where(where)
        
        if wherestr is not None:
            q = q.where(sqlalchemy.text(f'({wherestr})'))
        
        if order_by is not None:
            try:
                q = q.order_by(*order_by)
            except NotImplementedError:
                q = q.order_by(order_by)
            
        if group_by is not None:
            try:
                q = q.group_by(*group_by)
            except NotImplementedError:
                q = q.group_by(group_by)
            
        if limit is not None:
            q = q.limit(limit)
            
        if offset is not None:
            q = q.offset(offset)
            
        return q
    
    @staticmethod
    def update_query(
        table: sqlalchemy.Table,
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression], 
        wherestr: typing.Optional[str],
        **kwargs,
    ) -> sqlalchemy.sql.Update:
        
        q: sqlalchemy.sql.Update = sqlalchemy.sql.update(table, **kwargs)

        if where is not None:
            q = q.where(where)
            
        if wherestr is not None:
            q = q.where(sqlalchemy.text(wherestr))

        return q

    @staticmethod
    def insert_query(
        table: sqlalchemy.Table,
        ifnotunique: typing.Optional[typing.Literal['FAIL', 'IGNORE', 'REPLACE']],
    ) -> sqlalchemy.sql.Insert:
        q: sqlalchemy.sql.Insert = sqlalchemy.sql.insert(table)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        return q

    @staticmethod
    def delete_query(
        table: sqlalchemy.Table,
        where: typing.Optional[sqlalchemy.sql.expression.BinaryExpression] = None, 
        wherestr: typing.Optional[str] = None,
        **kwargs,
    ) -> sqlalchemy.sql.Delete:

        q: sqlalchemy.sql.Delete = sqlalchemy.sql.delete(table, **kwargs)

        if where is not None:
            q = q.where(where)

        if wherestr is not None:
            q = q.where(sqlalchemy.text(wherestr))

        return q


