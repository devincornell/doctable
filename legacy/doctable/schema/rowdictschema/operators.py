from __future__ import annotations

import typing
if typing.TYPE_CHECKING:
    from .schemaobject import SchemaObject


# this will be the member variable used underneath the hood
rowdict_attr_name = '_doctable_rowdict'


############# Main Getter/Setter Properties #############

def rowdict_has_attr(obj: SchemaObject, name: str) -> bool:
    '''Check if the rowdict has the provided key.'''
    return name in hasattr(obj, rowdict_attr_name)

def set_rowdict_attr(obj: SchemaObject, name: str, val: typing.Any) -> None:
    '''Set a particular rowdict attribute'''
    getattr(obj, rowdict_attr_name)[name] = val

def get_rowdict_attr(obj: SchemaObject, name: str) -> typing.Any:
    '''Get a rowdict attribute.'''
    return getattr(obj, rowdict_attr_name)[name]

def get_rowdict_attr_default(obj: SchemaObject, name: str, default: typing.Any) -> typing.Any:
    '''Get a rowdict attribute using .get() with the provided default.'''
    return getattr(obj, rowdict_attr_name).get(name, default)


def has_rowdict(obj: SchemaObject) -> bool:
    return hasattr(obj, rowdict_attr_name)

def set_rowdict(obj: SchemaObject, rowdict: typing.Dict) -> None:
    '''Set the rowdict associated with this object.'''
    return setattr(obj, rowdict_attr_name, rowdict)

def get_rowdict(obj: SchemaObject) -> typing.Dict:
    '''Get the rowdict associated with this object.'''
    return getattr(obj, rowdict_attr_name)

def rowdict_obj_from_dict(ObjType: type, d: typing.Dict) -> SchemaObject:
    return ObjType(_doctable_from_row_obj=d)

