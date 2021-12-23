
from doctable.schemas.parse_schema_dataclass import ColumnMetadata
from .emptyvalue import EmptyValue
from datetime import datetime
from dataclasses import dataclass, field, fields
from typing import Any, Union
import sqlalchemy

from .custom_coltypes import PickleFileType, ParseTreeDocFileType, TextFileType
            


def Col(column_type: Any = None, field_kwargs: dict = None, type_kwargs: dict = None, **column_kwargs):
    ''' Returns dataclasses.field() after setting convienient params.
    Args:
        field_kwargs: passed directly to dataclasses.field.
        **column_kwargs: passed to the sqlalchemy column object.
    '''
    if field_kwargs is None:
        field_kwargs = dict()

    if type_kwargs is None:
        type_kwargs = dict()

    if 'default' not in field_kwargs and 'default_factory' not in field_kwargs:
        field_kwargs['default'] = EmptyValue()

    column_metadata = ColumnMetadata(
        column_type = column_type,
        type_kwargs = type_kwargs,
        column_kwargs = column_kwargs,
    )

    return field(init=True, metadata={'column_metadata': column_metadata}, repr=True, **field_kwargs)

def IDCol():
    return Col(primary_key=True, autoincrement=True)

def UpdatedCol():
    ''' Column that will automatically update the date/time when the row is modified.
    '''
    return Col(default=datetime.now)

def AddedCol():
    ''' Column that will automatically update the date/time when the row is inserted.
    '''
    return Col(default=datetime.now, onupdate=datetime.now)

def PickleFileCol(folder, **kwargs):
    ''' Column that will store arbitrary python data in the filesystem and keep only a reference.
    '''
    return Col(column_type=PickleFileType, type_kwargs=dict(folder=folder), **kwargs)

def TextFileCol(folder, **kwargs):
    ''' Column that will store text data in the filesystem and keep only a reference.
    '''
    return Col(column_type=TextFileType, type_kwargs=dict(folder=folder), **kwargs)

def ParseTreeFileCol(folder, **kwargs):
    ''' Column that will store text data in the filesystem and keep only a reference.
    '''
    return Col(column_type=ParseTreeDocFileType, type_kwargs=dict(folder=folder), **kwargs)
    




