
import typing
import dataclasses
import datetime

from .column import Column, ColumnArgs, FieldArgs


@dataclasses.dataclass
class IDColTemplate:
    '''Template that includes the standard id field.'''
    id: int = Column(
        column_args=ColumnArgs(
            column_name='id', # name of the column in the db (might not want to have an attr called 'id')
            order = 0, # affects the ordering of the columns in the db
            primary_key=True,
            autoincrement=True,
        ),
    )

@dataclasses.dataclass
class IDAddedTemplate(IDColTemplate):
    '''Template that includes the standard id field.'''
    added: datetime.datetime = Column(
        column_args=ColumnArgs(
            order = float('inf'), 
            default=datetime.datetime.utcnow
        ),
        field_args = FieldArgs(repr=False),
    )

@dataclasses.dataclass
class IDAddedUpdatedTemplate(IDAddedTemplate):
    '''Template that includes the standard id field.'''    
    updated: datetime.datetime = Column(
        column_args=ColumnArgs(
            order = float('inf'), 
            default=datetime.datetime.now, 
            onupdate=datetime.datetime.now
        ),
        field_args = FieldArgs(repr=False)
    )

