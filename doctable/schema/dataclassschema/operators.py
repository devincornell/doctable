from __future__ import annotations
import typing
if typing.TYPE_CHECKING:
    from .doctableschema import DocTableSchema

from .missingvalue import MISSING_VALUE

PROPERTY_NAMES_ATTR = '__doctable_property_names__'

############# Convert to dictionaries and Tuples #############

def asdict(schema_obj: DocTableSchema) -> typing.Dict[str, typing.Any]:
    '''Convert the schema object to a dictionary.'''
    return {cn:getattr(schema_obj, pn) 
            for pn,cn in attr_map(schema_obj).items()}
    
def asdict_ignore_missing(schema_obj: DocTableSchema) -> typing.Dict[str, typing.Any]:
    '''Convert the schema object to a dictionary, ignoring missing values.'''
    return {cn:getattr(schema_obj, pn) 
            for pn,cn in attr_map(schema_obj).items() if getattr(schema_obj, pn) is not MISSING_VALUE}

def astuple(schema_obj: DocTableSchema) -> typing.Tuple[str, typing.Any]:
    return tuple(attr_map(schema_obj).items())

def attr_value_tuples(schema_obj: DocTableSchema) -> typing.Tuple[str, str, typing.Any]:
    return [(pn, an, getattr(schema_obj, pn)) for pn,an in attr_map(schema_obj)]


############# get and set property names dict #############
def attr_map(obj: DocTableSchema) -> typing.Dict[str,str]:
    '''Used to access property map to convert column name to underlying property name.'''
    return getattr(obj, PROPERTY_NAMES_ATTR)

def set_attr_map(obj: DocTableSchema, attr_names: typing.Dict[str, str]):
    '''Used to attach property names to a schema object.'''
    return setattr(obj, PROPERTY_NAMES_ATTR, attr_names)

def attr_value(obj: DocTableSchema, property_name: str) -> typing.Any:
    return getattr(obj, getattr(obj, PROPERTY_NAMES_ATTR)[property_name])


############# Convert between Column names and properties #############
def property_to_attr(pname: str) -> str:
    '''Convert column name to the property name.'''
    return f'_doctable__{pname}'

def attr_to_property(aname: str) -> str:
    '''Convert property name to column name.'''
    return '__'.join(aname.split('__')[1:])


