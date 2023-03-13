from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd

from .coltype_map import python_to_slqlchemy_type, string_to_sqlalchemy_type

@dataclasses.dataclass
class ColumnMetadata:
    '''Stores metadata from the user for conversion to an sqlalchemy column.'''
    column_type: typing.Union[str, type, sqlalchemy.sql.type_api.TypeEngine]
    type_kwargs: dict = None
    column_kwargs: dict = None

    def __post_init__(self):
        if self.type_kwargs is None:
            self.type_kwargs = dict()

        if self.column_kwargs is None:
            self.column_kwargs = dict()

    def get_sqlalchemy_col(self, name: str, type_hint: type) -> sqlalchemy.Column:
        coltype = self.get_sqlalchemy_type(type_hint)
        return sqlalchemy.Column(name, coltype, **self.column_kwargs)

    def get_sqlalchemy_type(self, type_hint: type):

        # has no column type information
        if self.column_type is None:
            #return python_to_slqlchemy_type.get(type_hint, sqlalchemy.PickleType)(**self.type_kwargs)
            try:
                type_obj = python_to_slqlchemy_type[type_hint]
            except KeyError as e:
                raise TypeError(f'The type hint "{type_hint}" is not in the set of valid column types. '
                    f'To use PickleType, provide the type hint "typing.Any". These are other valid types: '
                    f'{python_to_slqlchemy_type}') from e
            return type_obj(**self.type_kwargs)
            

        # is a string for a type
        elif isinstance(self.column_type, str):
            return string_to_sqlalchemy_type[self.column_type](**self.type_kwargs)
        
        # is sqlalchemy type definition
        elif isinstance(self.column_type, type):
            return self.column_type(**self.type_kwargs)

        # is instance of sqlalchemy type
        elif isinstance(self.column_type, sqlalchemy.sql.type_api.TypeEngine):

            if len(self.type_kwargs):
                raise ValueError('When passing an sqlalchemy type instance to column_type, '
                    'type_kwargs should be added to the type constructor directly.')

            return self.column_type
        
        else:
            raise ValueError(f'Unrecognized column type was provided: {self.column_type}')

