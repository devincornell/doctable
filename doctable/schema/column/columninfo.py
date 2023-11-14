from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

from .columnargs import ColumnArgs, get_column_args, has_column_args
from .column_types import ColumnTypeMatcher


@dataclasses.dataclass
class ColumnInfo:
    '''Contains all information needed to create a column in a database.'''
    attr_name: str # name of attribute in data container
    type_hint: type
    defined_order: int
    column_args: ColumnArgs
    
    @classmethod
    def default(cls, attr_name: str, type_hint: type) -> ColumnInfo:
        '''Get column info from only a sqlalchemy type.'''
        return cls(
            attr_name=attr_name,
            type_hint=type_hint,
            column_args=ColumnArgs(),
        )

    @classmethod
    def from_field(cls, field: dataclasses.Field, defined_order: int) -> ColumnInfo:
        '''Get column info from a dataclass field after dataclass is created.'''
        return cls(
            attr_name=field.name,
            type_hint=field.type,
            defined_order = defined_order,
            column_args=get_column_args(field) if has_column_args(field) else ColumnArgs(),
        )
    
    ############# Column Creation #############
    
    #def sqlalchemy_column(self) -> sqlalchemy.Column:
    #    '''Get a sqlalchemy column from this column info.'''
    #    return self.column_args.sqlalchemy_column(
    #        type_hint=self.type_hint,
    #        attr_name=self.attr_name,
    #    )
    def sqlalchemy_column(self, 
    ) -> sqlalchemy.Column:
        '''Get a sqlalchemy column from this column info.
            Raises KeyError if there is no match.
        '''
        return sqlalchemy.Column(
            self.final_name(),
            *self.column_type_args(),
            **self.column_args.sqlalchemy_column_kwargs(),
        )

    def column_type_args(self) -> typing.Union[typing.Tuple[sqlalchemy.ForeignKey], typing.Tuple[sqlalchemy.TypeClause, sqlalchemy.ForeignKey]]:
        fk = self.column_args.sqlalchemy_foreign_key()
        if fk is None:
            fk = tuple()
        else:
            fk = (sqlalchemy.ForeignKey(fk),)
        
        if self.column_args.sqlalchemy_type is not None:
            return (self.column_args.sqlalchemy_type,) + fk
        elif len(fk):
            return fk # infer column type from foreign key
        else:
            # sqlachemy type not provided and not a foreign key
            coltype = ColumnTypeMatcher.type_hint_to_column_type(self.type_hint)
            return (coltype(**self.column_args.type_kwargs),)
        

    def order_key(self) -> typing.Tuple[float, str]:
        '''Key used to generate column ordering.'''
        return (self.column_args.order, self.defined_order)
    
    
    ############# Names #############
    def name_translation(self) -> typing.Tuple[str, str]:
        '''Get (attribute, column) name pairs.'''
        return self.attr_name, self.final_name()
    
    def final_name(self) -> str:
        if self.column_args.column_name is None:
            return self.attr_name
        else:
            return self.column_args.column_name

    ############# For inspection #############
    def info_dict(self) -> typing.Dict[str, typing.Any]:
        '''Get a human-readable dictionary of information about this column.'''
        return {
            'Column Name': self.final_name(),
            'Attribute Name': self.attr_name,
            'Type Hint': self.type_hint,
            'SQLAlchemy Type': self.column_args.sqlalchemy_type,
            'Order': self.column_args.order,
            'Primary Key': self.column_args.primary_key,
            'Index': self.column_args.index,
            'Default': self.column_args.default,
        }
