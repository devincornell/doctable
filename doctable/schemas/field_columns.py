
from .emptyvalue import EmptyValue
from datetime import datetime
from dataclasses import dataclass, field, fields


def Col(obj_default=EmptyValue(), **colargs):
    ''' Returns .field() after setting convienient params.
    Args:
        obj_default (any): default value of the object property.
            NOT stored in database, just set when returning select 
            query and the value was not requested. By leaving at
            EmptyValue(), will throw an error when subscripting.
        **colargs: passed to the sqlalchemy column object.
    '''
    if callable(obj_default):
        default_arg = {'default_factory': obj_default}
    else:
        default_arg = {'default': obj_default}
    return field(init=True, metadata=colargs, repr=True, **default_arg)

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
    return Col(None, coltype='picklefile', type_args=dict(folder=folder), **kwargs)

def TextFileCol(folder, **kwargs):
    ''' Column that will store text data in the filesystem and keep only a reference.
    '''
    return Col(None, coltype='textfile', type_args=dict(folder=folder), **kwargs)


