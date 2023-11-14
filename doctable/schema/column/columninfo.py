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
        elif self.column_args.use_type is not None:
            coltype = ColumnTypeMatcher.type_hint_to_column_type(self.column_args.use_type)
            return (coltype(**self.column_args.type_kwargs),)
        else:
            # sqlachemy type not provided and not a foreign key
            coltype = ColumnTypeMatcher.type_hint_to_column_type(self.type_hint)
            return (coltype(**self.column_args.type_kwargs),)
    
    def estimate_sqlalchemy_type(self) -> sqlalchemy.TypeClause:
        '''Guess sqlclehmy type here - use column_type_args for correct version.'''
        if self.column_args.sqlalchemy_type is not None:
            return self.column_args.sqlalchemy_type
        elif self.column_args.use_type is not None:
            return ColumnTypeMatcher.type_hint_to_column_type(self.column_args.use_type)
        else:
            return ColumnTypeMatcher.type_hint_to_column_type(self.type_hint)
    
    
    ############# Names #############
    def name_translation(self) -> typing.Tuple[str, str]:
        '''Get (attribute, column) name pairs.'''
        return self.attr_name, self.final_name()
    
    def final_name(self) -> str:
        if self.column_args.column_name is None:
            return self.attr_name
        else:
            return self.column_args.column_name
        
    def order_key(self) -> typing.Tuple[float, str]:
        '''Key used to generate column ordering.'''
        return (self.column_args.order, self.defined_order)

    ############# For inspection #############
    def info_dict(self) -> typing.Dict[str, typing.Any]:
        '''Get a human-readable dictionary of information about this column.'''
        try:
            col_type = self.estimate_sqlalchemy_type().__name__
        except AttributeError as e:
            col_type = self.estimate_sqlalchemy_type().__class__.__name__
            
        default = self.column_args.default
        return {
            'Col Name': self.final_name(),
            'Col Type': col_type,
            'Attr Name': self.attr_name,
            'Hint': self.type_hint.__name__,
            'Order': self.order_key(),
            'Primary Key': self.column_args.primary_key,
            'Foreign Key': self.column_args.foreign_key is not None,
            'Index': self.column_args.index,
            'Default': default.__name__ if default is not None else None,
        }
