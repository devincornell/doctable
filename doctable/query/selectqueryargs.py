from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd

from ..util import is_sequence
from ..doctable import DocTable
from ..schemas import DocTableSchema
from .basequery import BaseQuery


@dataclasses.dataclass
class SelectQueryArgs:
    cols: typing.List[sqlalchemy.Column]
    where: sqlalchemy.sql.expression.BinaryExpression = None
    orderby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None
    groupby: typing.Union[sqlalchemy.Column, typing.List[sqlalchemy.Column]] = None
    limit: int = None
    wherestr: str = None
    offset: int = None
    
    def get_query(self) -> sqlalchemy.sql.Select:
        '''Build and exectute select query given all the conditionals provided as parameters.'''
        
        q: sqlalchemy.sql.Select = sqlalchemy.sql.select(self.cols)
        
        if self.where is not None:
            q = q.where(self.where)
        
        if self.wherestr is not None:
            q = q.where(sqlalchemy.text(f'({self.wherestr})'))
        
        if self.orderby is not None:
            if is_sequence(self.orderby):
                q = q.order_by(*self.orderby)
            else:
                q = q.order_by(self.orderby)
        
        if self.groupby is not None:
            if is_sequence(self.groupby):
                q = q.group_by(*self.groupby)
            else:
                q = q.group_by(self.groupby)
            
        if self.limit is not None:
            q = q.limit(self.limit)
            
        if self.offset is not None:
            q = q.offset(self.offset)
            
        return q
    
    
    