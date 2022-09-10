
import datetime
from doctable.schemas.constraints import Constraint
import sqlalchemy
from dataclasses import dataclass, field, fields
from .coltype_map import python_to_slqlchemy_type, string_to_sqlalchemy_type, constraint_lookup
from .constraints import Constraint
from typing import Union, Any, List, Tuple
from .errors import *

def parse_schema_dataclass(Cls, indices: Tuple[sqlalchemy.Index], constraints: Tuple[Constraint]):
    ''' Convert a dataclass definition to a list of sqlalchemy columns.
    '''
    return parse_columns(Cls) + parse_indices(indices) + parse_constraints(constraints)


@dataclass
class ColumnMetadata:
    column_type: Union[str, type, sqlalchemy.sql.type_api.TypeEngine]
    type_kwargs: dict = None
    column_kwargs: dict = None

    def __post_init__(self):
        if self.type_kwargs is None:
            self.type_kwargs = dict()

        if self.column_kwargs is None:
            self.column_kwargs = dict()

    @property
    def has_type(self):
        return self.column_type is not None

    def get_sqlalchemy_type(self, type_hint: type):

        # has no column type information
        if self.column_type is None:
            #try:
            return python_to_slqlchemy_type.get(type_hint, sqlalchemy.PickleType)(**self.type_kwargs)
            #except KeyError as e:
            #    raise TypeNotRecognizedError(f'The type "{type_hint}" does not have a corresponding '
            #        'sqlalchemy datatype. If unsure and unconcerned with performance, use typing.Any '
            #        '(which resolves to sqlalchemy.PickleType).')

        # is a string for a type
        elif isinstance(self.column_type, str):
            return string_to_sqlalchemy_type[self.column_type](**self.type_kwargs)
        
        # is sqlalchemy type definition
        elif isinstance(self.column_type, type):
            return self.column_type(**self.type_kwargs)

        # is instance of sqlalchemy type
        elif isinstance(self.column_type, sqlalchemy.sql.type_api.TypeEngine):

            if len(self.type_kwargs):
                raise ValueError('When passing an sqlalchemy type instance to column_type, '
                    'type_kwargs should be added to the type constructor directly.')

            return self.column_type
        
        else:
            raise ValueError(f'Unrecognized column type was provided: {self.column_type}')



def parse_columns(Cls):
    ''' Convert the dataclass member variables to sqlalchemy columns.
    '''
    columns = list()
    for f in fields(Cls):
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


#_indices_ = {
#    'my_index': ('c1', 'c2', {'unique':True}),
#    'other_index': ('c1',),
#}
def parse_indices(indices):
    return list(indices)

#_constraints_ = (
#    ('check', 'x > 3', dict(name='salary_check')), 
#    ('foreignkey', ('a','b'), ('c','d'))
#)
#if hasattr(Cls, '_constraints_') and Cls._constraints_ is not None:
def parse_constraints(constraints):
    return list(constraints)
    #columns = list()
    #for vals in constraints:
    #    args, kwargs = get_kwargs(vals)
    #    columns.append(constraint_lookup[args[0]](*args[1:], **kwargs))

    return columns


#def get_kwargs(vals):
#    ''' Logic to parse out ordered and keyword arguments.
#    '''
#    args = vals[:-1] if isinstance(vals[-1], dict) else vals
#    kwargs = vals[-1] if isinstance(vals[-1], dict) else dict()
#    #print(f'args={args}, kwargs={kwargs}')
#    return args, kwargs
