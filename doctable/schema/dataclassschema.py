from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import copy

from ..schemas import DocTableSchema, MISSING_VALUE
from .schemabase import SchemaBase
from .columnmetadata import ColumnMetadata
from ..schemas import Constraint, python_to_slqlchemy_type

@dataclasses.dataclass
class DataclassSchema(SchemaBase):
    columns: typing.List[sqlalchemy.Column]
    schema_class: type[DocTableSchema]
    indices: typing.Tuple[sqlalchemy.Index]
    constraints: typing.Tuple[Constraint]
    
    @classmethod
    def from_schema_definition(cls, schema_class: type[DocTableSchema], indices: typing.Tuple[sqlalchemy.Index], constraints: typing.Tuple[Constraint]):
        ''' Convert a dataclass definition to a list of sqlalchemy columns.
        '''
        if not issubclass(schema_class, DocTableSchema):
            raise TypeError('A dataclass schema must inherit from doctable.DocTableSchema.')
            
        new_schema: cls = cls(
            columns = cls.parse_columns(schema_class) + cls.parse_indices(indices) + cls.parse_constraints(constraints),
            schema_class = copy.deepcopy(schema_class),
            indices = copy.deepcopy(indices),
            constraints = copy.deepcopy(constraints),
        )
        return new_schema
    
    def object_to_dict(self, obj: DocTableSchema) -> typing.Dict:
        #try:
        #    return {f.name:getattr(self,f.name) for f in dataclasses.fields(obj) 
        #                                if self.get_val(f.name) is not MISSING_VALUE}
        #except AttributeError:
        try:
            return {f.name:getattr(self,f.name) for f in dataclasses.fields(self.schema_class) 
                                        if getattr(self,f.name) is not MISSING_VALUE}
        except AttributeError as e:
            missing_attrs = {f.name:hasattr(self,f.name) for f in dataclasses.fields(self.schema_class)}
            raise AttributeError(f'{type(obj)} object to be inserted does not have '
                f'required attributes. These attributes are missing: {missing_attrs=}') from e
    
    def row_to_object(self, row: sqlalchemy.engine.row.LegacyRow) -> typing.Any:
        return self.schema_class(**dict(row))
    

    def parse_columns(Cls):
        ''' Convert the dataclass member variables to sqlalchemy columns.
        '''
        columns = list()
        for f in dataclasses.fields(Cls):
            if f.init:

                if 'column_metadata' in f.metadata:

                    column_metadata: ColumnMetadata = f.metadata['column_metadata']

                    # if column metadata was provided
                    use_type = column_metadata.get_sqlalchemy_type(f.type)
                    col = sqlalchemy.Column(f.name, use_type, **column_metadata.column_kwargs)
                
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
        