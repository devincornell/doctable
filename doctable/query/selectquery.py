from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..doctable import DocTable


import sqlalchemy
import dataclasses
import typing
import pandas as pd



from ..schema import DocTableSchema
from ..util import is_sequence

from .errors import *
from .querybase import QueryBase



class SelectQuery:
    dtab: DocTable

    ######################################## Compound Selects ########################################
    
    def select_iter(self, cols=None, chunksize=1, limit=None, **kwargs):
        ''' Same as .select except results retrieved from db in chunks.
        Args:
            cols (col name(s) or sqlalchemy object(s)): columns to query
            chunksize (int): size of individual queries to be made. Will
                load this number of rows into memory before yielding.
            limit (int): maximum number of rows to retrieve. Because 
                the limit argument is being used internally to limit data
                to smaller chunks, use this argument instead. Internally,
                this function will load a maximum of limit + chunksize 
                - 1 rows into memory, but yields only limit.
        Yields:
            sqlalchemy result: row data - same as .select() method.
        '''
        for chunk in self.select_chunks(cols=cols, chunksize=chunksize, 
                                                    limit=limit, **kwargs):
            for row in chunk:
                yield row
    
    def select_chunks(self, cols: typing.List[typing.Union[str, sqlalchemy.Column]] = None, chunksize: int = 100, limit: int = None, raw_result: bool = False, **kwargs):
        ''' Performs select while querying only a subset of the results at a time.
        Args:
            cols (col name(s) or sqlalchemy object(s)): columns to query
            chunksize (int): size of individual queries to be made. Will
                load this number of rows into memory before yielding.
            limit (int): maximum number of rows to retrieve. Because 
                the limit argument is being used internally to limit data
                to smaller chunks, use this argument instead. Internally,
                this function will load a maximum of limit + chunksize 
                - 1 rows into memory, but yields only limit.
        Yields:
            result: chunked rows.
        '''
        select_func = self.select_raw if raw_result else self.select
        
        offset = 0
        while True:
            
            rows = select_func(cols, offset=offset, limit=chunksize, **kwargs)
            chunk = rows[:limit-offset] if limit is not None else rows
            
            yield chunk
            
            offset += len(rows)
            
            if (limit is not None and offset >= limit) or len(rows) == 0:
                break

    ######################################## Counting ########################################
    
    def count(self, 
            where: sqlalchemy.sql.expression.BinaryExpression = None, 
            wherestr: str = None, 
            **kwargs
        ) -> int:
        '''Count the number of rows in a table.'''
        cter = sqlalchemy.func.count(self.dtab.columns[0])
        ct = self.select_col(cter, where=where, wherestr=wherestr, limit=1, **kwargs)

        return ct[0]
    
    ######################################## Select to Pandas Objects ########################################

    def select_head(self, n: int = 5, **kwargs) -> pd.DataFrame:
        return self.select_df(limit=n, **kwargs)
        
    def select_series(self,
            col: typing.Union[str, sqlalchemy.Column],
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
            **kwargs
        ) -> pd.Series:
        '''Select returning pandas Series.
        Args:
            col: column to query. Passed directly to .select() 
                method.
            *args: args to regular .select() method.
            **kwargs: args to regular .select() method.
        Returns:
            pandas series: enters rows as values.
        '''
        return pd.Series(self.select_col(
            col = col,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            **kwargs
        ))
        
    def select_df(self, 
            cols: typing.List[typing.Union[str, sqlalchemy.Column]] = None,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
            **kwargs
        ) -> pd.DataFrame:
        '''Select returning dataframe.
        Args:
            cols: sequence of columns to query. Must be sequence,
                passed directly to .select() method.
            *args: args to regular .select() method.
            **kwargs: args to regular .select() method.
        Returns:
            pandas dataframe: Each row is a database row,
                and output is not indexed according to primary 
                key or otherwise. Call .set_index('id') on the
                dataframe to envoke this behavior.
        '''
        return pd.DataFrame(self.select_raw(
            cols = self.parse_input_cols(cols),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            **kwargs
        ))
        


    ######################################## Single row/col Select Functions ########################################
    def select_scalar(self, 
            col: typing.Union[str, sqlalchemy.Column],
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            wherestr: str = None,
            offset: int = None,
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
            col: typing.Union[str, sqlalchemy.Column],
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
            **kwargs
        ) -> typing.List[typing.Any]:
        '''Select values of a single column.'''
        
        rows = self.select_raw(
            cols = self.parse_input_col(col),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            **kwargs
        )
        return [r[0] for r in rows]

    def select_first(self,
            cols: typing.List[typing.Union[str, sqlalchemy.Column]] = None,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            wherestr: str = None,
            offset: int = None,
            raw_result: bool = False, 
            **kwargs
        ) -> DocTableSchema:
        
        select_func = self.select if not raw_result else self.select_raw
        results = select_func(
            cols = cols,
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = 1,
            wherestr = wherestr,
            offset = offset,
            **kwargs
        )
        
        if len(results) == 0:
            raise LookupError('No results were returned. Needed to error '
                'so this result wasn not confused with case where actual '
                'result is None. If not sure about result, use regular '
                '.select() method with limit=1.')

        return results[0]

    ################################ Base Select Methods ################################
    def select(self, 
            cols: typing.List[sqlalchemy.Column] = None,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
            **kwargs
        ) -> typing.List[DocTableSchema]:
        '''
        Select some basic shit.
        Description: Because output must be iterable, returns special column results 
            by performing one query per row. Can be inefficient for many smaller 
            special data information.
        
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
            wherestr (str): raw sql "where" conditionals to add to where input
            **kwargs: passed to self.execute()
        Yields:
            sqlalchemy result object: row data

        '''
        results = self.select_raw(
            cols = self.parse_input_cols(cols),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
            **kwargs
        )
        return [self.dtab.schema.row_to_object_interface(r) for r in results]

    def select_raw(self, 
            cols: typing.List[sqlalchemy.Column] = None,
            where: sqlalchemy.sql.expression.BinaryExpression = None,
            orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
            limit: int = None,
            wherestr: str = None,
            offset: int = None,
            **kwargs
        ) -> typing.List[typing.Dict[str, typing.Any]]:
        '''
        Select some basic shit.
        Description: Because output must be iterable, returns special column results 
            by performing one query per row. Can be inefficient for many smaller 
            special data information.
        
        Args:
            cols: list of sqlalchemy datatypes created from calling .col() method.
            where (sqlachemy BinaryExpression): sqlalchemy "where" object to parse
            orderby: sqlalchemy orderby directive
            groupby: sqlalchemy gropuby directive
            limit (int): number of entries to return before stopping
            wherestr (str): raw sql "where" conditionals to add to where input
            **kwargs: passed to self.execute()
        Yields:
            sqlalchemy result object: row data

        '''
        q = self.select_query(
            cols = self.parse_input_cols(cols),
            where = where,
            orderby = orderby,
            groupby = groupby,
            limit = limit,
            wherestr = wherestr,
            offset = offset,
        )
        
        return self.dtab.execute(q, **kwargs).fetchall()
    
    @staticmethod
    def select_query(
        cols: typing.List[sqlalchemy.Column],
        where: sqlalchemy.sql.expression.BinaryExpression = None,
        orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
        groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None,
        limit: int = None,
        wherestr: str = None,
        offset: int = None,
    ) -> sqlalchemy.sql.Select:
        '''Build and exectute select query given all the conditionals provided as parameters.'''
        
        q: sqlalchemy.sql.Select = sqlalchemy.sql.select(cols)
        
        if where is not None:
            q = q.where(where)
        
        if wherestr is not None:
            q = q.where(sqlalchemy.text(f'({wherestr})'))
        
        if orderby is not None:
            if is_sequence(orderby):
                q = q.order_by(*orderby)
            else:
                q = q.order_by(orderby)
        
        if groupby is not None:
            if is_sequence(groupby):
                q = q.group_by(*groupby)
            else:
                q = q.group_by(groupby)
            
        if limit is not None:
            q = q.limit(limit)
            
        if offset is not None:
            q = q.offset(offset)
            
        return q
    

    ############################## Parse User Input ##############################
    def parse_input_cols(self, cols: typing.List[typing.Union[str, sqlalchemy.Column]]) -> typing.List[sqlalchemy.Column]:
        '''Pass variable passed to cols.'''        
        if cols is None:
            cols = list(self.dtab.columns)
        else:
            if not is_sequence(cols):
                raise TypeError('cols argument should be a list of columns.')

            cols = [self.dtab.col(c) if isinstance(c,str) else c for c in cols]
        
        return cols
    
    def parse_input_col(self, col: typing.Union[str, sqlalchemy.Column]) -> typing.List[sqlalchemy.Column]:
        if is_sequence(col):
            raise TypeError('col argument should be single column.')
        
        use_col = self.dtab.col(col) if isinstance(col,str) else col
        return [use_col]


