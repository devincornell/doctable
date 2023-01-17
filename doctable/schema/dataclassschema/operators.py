from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from .doctableschema import DocTableSchema

from .missingvalue import MISSING_VALUE

PROPERTY_NAMES_ATTR = '__doctable_property_names__'

############# Convert to dictionaries and Tuples #############

def asdict(schema_obj: DocTableSchema) -> typing.Dict[str, typing.Any]:
    '''Convert the schema object to a dictionary.'''
    return {pn:getattr(schema_obj, an) 
            for pn,an in get_attr_map(schema_obj).items()}
    
def asdict_ignore_missing(schema_obj: DocTableSchema) -> typing.Dict[str, typing.Any]:
    '''Convert the schema object to a dictionary, ignoring missing values.'''
    return {pn:getattr(schema_obj, an) 
            for pn,an in get_attr_map(schema_obj).items() if getattr(schema_obj, an) is not MISSING_VALUE}

def astuple(schema_obj: DocTableSchema) -> typing.Tuple[str, typing.Any]:
    return tuple(asdict(schema_obj).items())

def attr_value_tuples(schema_obj: DocTableSchema) -> typing.Tuple[str, str, typing.Any]:
    return [(pn, an, getattr(schema_obj, an)) for pn,an in get_attr_map(schema_obj).items()]

def as_value_tuple(schema_obj: DocTableSchema) -> typing.Tuple[str, str, typing.Any]:
    return tuple(getattr(schema_obj, an) for pn,an in get_attr_map(schema_obj).items())

############# get and set property names dict #############
def has_attr_map(obj: DocTableSchema) -> typing.Dict[str,str]:
    '''Used to access property map to convert column name to underlying property name.'''
    return hasattr(obj, PROPERTY_NAMES_ATTR)

def get_attr_map(obj: DocTableSchema) -> typing.Dict[str,str]:
    '''Used to access property map to convert column name to underlying property name.'''
    return getattr(obj, PROPERTY_NAMES_ATTR)

def set_attr_map(obj: DocTableSchema, attr_map: typing.Dict[str, str]):
    '''Used to attach property names to a schema object.'''
    return setattr(obj, PROPERTY_NAMES_ATTR, attr_map)

def attr_value(obj: DocTableSchema, property_name: str) -> typing.Any:
    return getattr(obj, getattr(obj, PROPERTY_NAMES_ATTR)[property_name])


############# Convert between Column names and properties #############
def property_to_attr(pname: str) -> str:
    '''Convert column name to the property name.'''
    return f'_doctable__{pname}'

def attr_to_property(aname: str) -> str:
    '''Convert property name to column name.'''
    return '__'.join(aname.split('__')[1:])


