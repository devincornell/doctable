from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from .tableschema import TableSchema

Container = typing.TypeVar('Container')

# name of Schema type attribute that will store the parsed table schema object
SCHEMA_ATTRIBUTE_NAME = '_table_schema'

def set_schema(Cls: typing.Type[Container], schema: TableSchema[Container]) -> None:
    return setattr(Cls, SCHEMA_ATTRIBUTE_NAME, schema)

def get_schema(Cls: typing.Type[Container]) -> TableSchema[Container]:
    return getattr(Cls, SCHEMA_ATTRIBUTE_NAME)

