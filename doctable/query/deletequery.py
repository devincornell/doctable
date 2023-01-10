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



class DeleteQuery(QueryBase):
    dtab: DocTable

    ############################## Delete Methods ##############################
    
    def delete(self, 
            where: sqlalchemy.sql.expression.BinaryExpression = None, 
            wherestr: str = None,
            delete_all: bool = False, 
            vacuum: bool = False,
            **kwargs,
        ) -> sqlalchemy.engine.ResultProxy:
        '''Delete rows from the table that meet the where criteria.
        Args:
            where (sqlalchemy condition): criteria for deletion.
            wherestr (sql string): addtnl criteria for deletion.
            vacuum (bool): will execute vacuum sql command to reduce
                storage space needed by SQL table. Use when deleting
                significant ammounts of data.
        Returns:
            SQLAlchemy result proxy object.
        '''
        self._check_readonly('delete')
        
        if where is None and wherestr is None and not delete_all:
            raise ValueError(f'Must set delete_all=True to delete all rows. This is '
                'a safety precaution.')
        
        q = self.delete_query(
            where = where,
            wherestr = wherestr,
        )
        
        r = self.dtab.execute(q, **kwargs)
        
        if vacuum:
            self.dtab.execute('VACUUM')
        
        # https://kite.com/python/docs/sqlalchemy.engine.ResultProxy
        return r
    
    def delete_query(self,
        where: sqlalchemy.sql.expression.BinaryExpression = None, 
        wherestr: str = None,
        **kwargs,
    ) -> sqlalchemy.sql.Delete:

        q: sqlalchemy.sql.Delete = sqlalchemy.sql.delete(
            self.dtab.table, 
            **kwargs,
        )

        if where is not None:
            q = q.where(where)
        if wherestr is not None:
            q = q.where(sqlalchemy.text(wherestr))

        return q

