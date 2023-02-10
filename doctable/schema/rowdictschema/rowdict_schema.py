from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import copy
import attrs
import warnings

from ...util import parse_static_arg
from ..schemabase import SchemaBase
from .schemaobject import SchemaObject
from .operators import set_rowdict, get_rowdict
#from .columnmetadata import ColumnMetadata
#from .doctableschema import DocTableSchema

from ..coltype_map import python_to_slqlchemy_type
#from .doctableschema import DocTableSchema
#from .operators import asdict_ignore_missing
from ..dataclassschema import Index, Constraint
from ..columnmetadata import ColumnMetadata

@dataclasses.dataclass
class RowDictSchema(SchemaBase):
    '''Contains info about the db schema and methods to convert to/from schema objects.'''
    schema_class: type[SchemaObject]
    columns: typing.List[sqlalchemy.Column]
    indices: typing.Tuple[Index]
    constraints: typing.Tuple[Constraint]
    
    @classmethod
    def from_schema_definition(cls, 
            schema_class: type[SchemaObject], 
            indices: typing.List[Index] = None, 
            constraints: typing.Tuple[Constraint] = None
        ):
        ''' Convert a dataclass definition to a list of sqlalchemy columns.
        '''
        if not issubclass(schema_class, SchemaObject):
            raise TypeError('A SchemaObject must inherit from doctable. '
                'SchemaObject. Did you use the schema decorator?.')
        
        # get them as part of schema class potentially
        indices = parse_static_arg(schema_class, indices, 'indices', '_indices_', tuple())
        constraints = parse_static_arg(schema_class, constraints, 'constraints', '_constraints_', tuple())
        
        new_schema: cls = cls(
            schema_class = copy.deepcopy(schema_class),
            columns = cls.parse_columns(schema_class),
            indices = cls.parse_indices(copy.deepcopy(indices)),
            constraints = cls.parse_constraints(copy.deepcopy(constraints)),
        )
        return new_schema
    
    def object_to_dict(self, obj: SchemaObject) -> typing.Dict:
        return get_rowdict(obj)
    
    def row_to_object(self, row: sqlalchemy.engine.row.LegacyRow) -> typing.Any:
        return self.schema_class(_doctable_from_row_obj=row)

    def parse_columns(Cls) -> typing.List[sqlalchemy.Column]:
        ''' Convert the dataclass member variables to sqlalchemy columns.
        '''
        columns = list()
        for f in attrs.fields(Cls):
            if f.init:

                if 'column_metadata' in f.metadata:

                    column_metadata: ColumnMetadata = f.metadata['column_metadata']
                    col = column_metadata.get_sqlalchemy_col(f.name, f.type)
                    
                    # if column metadata was provided
                    #use_type = column_metadata.get_sqlalchemy_type(f.type)
                    #col = sqlalchemy.Column(f.name, use_type, **column_metadata.column_kwargs)
                
                # if no ColumnMetadata was passed
                else:
                    use_type = python_to_slqlchemy_type.get(f.type, sqlalchemy.PickleType)
                    col = sqlalchemy.Column(f.name, use_type)
                
                columns.append(col)

        return columns


    def parse_indices(indices):
        return tuple(indices)

    def parse_constraints(constraints):
        return list(constraints)
        
