from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd

from ..schemas import DocTableSchema
from .schemabase import SchemaBase
from .columnmetadata import ColumnMetadata
from ..schemas import Constraint, python_to_slqlchemy_type

@dataclasses.dataclass
class ObjectSchema(SchemaBase):
    columns: typing.List[sqlalchemy.Column]
    
    @classmethod
    def from_schema_definition(cls, schema_class: type[DocTableSchema], indices: typing.Tuple[sqlalchemy.Index], constraints: typing.Tuple[Constraint]):
        ''' Convert a dataclass definition to a list of sqlalchemy columns.
        '''
        new_schema: cls = cls(
            columns = cls.parse_columns(schema_class) + cls.parse_indices(indices) + cls.parse_constraints(constraints)
        )
        return new_schema
    
    def object_to_dict(self, obj: DocTableSchema) -> typing.Dict:
        return obj._doctable_as_dict()
    
    def dict_to_object(self, data: typing.Dict[str, typing.Any]) -> typing.Any:
        return DocTableSchema._doctable_from_db(data)

    def parse_columns(Cls):
        ''' Convert the dataclass member variables to sqlalchemy columns.
        '''
        columns = list()
        for f in dataclasses.fields(Cls):
            if f.init:

                if 'column_metadata' in f.metadata:

                    metadata = f.metadata['column_metadata']

                    # if column metadata was provided
                    if isinstance(metadata, ColumnMetadata):
                        use_type = metadata.get_sqlalchemy_type(f.type)
                        col = sqlalchemy.Column(f.name, use_type, **metadata.column_kwargs)
                
                # if no ColumnMetadata was passed
                else:
                    use_type = python_to_slqlchemy_type.get(f.type, sqlalchemy.PickleType)
                    col = sqlalchemy.Column(f.name, use_type)
                
                columns.append(col)

        return columns


    def parse_indices(indices):
        return list(indices)

    def parse_constraints(constraints):
        return list(constraints)
        
