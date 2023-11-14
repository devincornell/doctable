from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime



from datetime import date, time, datetime
from typing import Any

def type_mappings() -> typing.Dict[typing.Union[typing.Type,str], typing.Type[sqlalchemy.TypeClause]]:
    return ColumnTypeMatcher.type_hint_to_column_type_mapping

class ColumnTypeMatcher:
    type_hint_to_column_type_mapping = {
        int: sqlalchemy.Integer,
        float: sqlalchemy.Float,
        bool: sqlalchemy.Boolean,
        str: sqlalchemy.String,
        bytes: sqlalchemy.LargeBinary,
        datetime: sqlalchemy.DateTime, # NOTE: datetime.datetime is subclass of datetime.date, so put it first
        time: sqlalchemy.Time,
        date: sqlalchemy.Date,
        Any: sqlalchemy.PickleType,
        'datetime.datetime': sqlalchemy.DateTime, # NOTE: datetime.datetime is subclass of datetime.date
        'datetime.time': sqlalchemy.Time, # NOTE: datetime.datetime is subclass of datetime.date
        'datetime.date': sqlalchemy.Date, # NOTE: datetime.datetime is subclass of datetime.date
        'Any': sqlalchemy.PickleType,
    }

    @classmethod
    def type_hint_to_column_type(cls, type_hint: typing.Union[typing.Type, str]) -> typing.Type[sqlalchemy.TypeClause]:
        '''Match type hint to sqlalchemy column type.'''
        for mth, mct in cls.type_hint_to_column_type_mapping.items():
            if cls.type_hint_matches(type_hint, mth):
                #return (mct(**self.type_kwargs),)
                return mct
        raise TypeError(f'"{type_hint}" does not map to a valid column '
            f'type. Choose one of {cls.type_hint_to_column_type_mapping.keys()}')
            
    @staticmethod
    def type_hint_matches(type_hint: typing.Union[typing.Type, str], match_type_hint: typing.Type) -> bool:
        '''Check if supplied type hint matches the given candidate.'''
        
        if type_hint == str(match_type_hint):
            return True
        
        try:
            if type_hint == match_type_hint.__name__:
                return True
        except AttributeError as e:
            pass
        
        try:
            if issubclass(type_hint, match_type_hint): # type: ignore
                return True
            
        except TypeError as e:
            return False

        return False



