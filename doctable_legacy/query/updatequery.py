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

class UpdateQuery(QueryBase):
    dtab: DocTable

    ############################## Update Methods ##############################
    def update(self, 
            values: typing.Dict[typing.Union[str,sqlalchemy.Column], typing.Any], 
            where: sqlalchemy.sql.expression.BinaryExpression = None, 
            wherestr: str = None,
            **kwargs
        ) -> sqlalchemy.engine.ResultProxy:
        '''Update row(s) assigning the provided values.
        Args:
            values (dict<colname->value> or list<dict> or list<(col,value)>)): 
                values to populate rows with. If dict, will insert those values
                into all rows that match conditions. If list of dicts, assigns
                expression in value (i.e. id['year']+1) to column. If list of 
                (col,value) 2-tuples, will assign value to col in the order 
                provided. For example given row values x=1 and y=2, the input
                [(x,y+10),(y,20)], new values will be x=12, y=20. If opposite
                order [(y,20),(x,y+10)] is provided new values would be y=20,
                x=30. In cases where list<dict> is provided, this behavior is 
                undefined.
            where (sqlalchemy condition): used to match rows where
                update will be applied.
            wherestr (sql string condition): matches same as where arg.
        Returns:
            SQLAlchemy result proxy object
        '''
        self._check_readonly('update')
        
        q = self.update_query(
            where = where,
            wherestr = wherestr,
            preserve_parameter_order = is_sequence(values),
        )
        
        q = q.values(values)
         
        return self.dtab.execute(q, **kwargs)

    def update_query(self,
        where: sqlalchemy.sql.expression.BinaryExpression = None, 
        wherestr: str = None,
        **kwargs,
    ) -> sqlalchemy.sql.Update:

        q: sqlalchemy.sql.Update = sqlalchemy.sql.update(
            self.dtab.table, 
            **kwargs,
        )

        if where is not None:
            q = q.where(where)
        if wherestr is not None:
            q = q.where(sqlalchemy.text(wherestr))

        return q

