
import datetime
import sqlalchemy
from dataclasses import dataclass, field, fields
from .coltype_map import python_to_slqlchemy_type, string_to_sqlalchemy_type, constraint_lookup
from typing import Union, Any

def parse_schema_dataclass(Cls, indices: dict, constraints: list):
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
            return python_to_slqlchemy_type.get(type_hint, sqlalchemy.PickleType)(**self.type_kwargs])

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
            #metadata = f.metadata
            if isinstance(f.metadata, ColumnMetadata):
                use_type = f.metadata.get_sqlalchemy_type(f.type)
            else:
                use_type = python_to_slqlchemy_type.get(f.type, sqlalchemy.PickleType)




            # if default value is not a doctable.Col or field
            if not isinstance(metadata, ColumnMetadata):
                use_type = python_to_slqlchemy_type.get(f.type, sqlalchemy.PickleType)

            else:

                
                # infer column type from python type hint
                if metadata['column_type'] is None:
                    use_type = python_to_slqlchemy_type.get(f.type, sqlalchemy.PickleType)(**metadata['type_kwargs'])
                
                # column type was provided directly
                else:
                    
                    # string type was passed
                    if isinstance(metadata['column_type'], str):
                        use_type = string_to_sqlalchemy_type[metadata['column_type']](**metadata['type_kwargs'])

                    else:

                        # sqlalchemy type instance was passed
                        if isinstance(metadata['column_type'], sqlalchemy.sql.type_api.TypeEngine):
                            if metadata['type_kwargs'] is not None:
                                raise ValueError('When passing an sqlalchemy type instance to column_type, '
                                    'type_kwargs should be added to the type constructor directly.')

                            use_type = metadata['column_type']

                        # sqlalchemy type definition was passed
                        else:
                            use_type = metadata['column_type'](**metadata['type_kwargs'])
            
            col = sqlalchemy.Column(f.name, use_type, **metadata['column_kwargs'])
            columns.append(col)

    return columns


#_indices_ = {
#    'my_index': ('c1', 'c2', {'unique':True}),
#    'other_index': ('c1',),
#}
def parse_indices(indices):
    columns = list()
    for name, vals in indices.items():
        args, kwargs = get_kwargs(vals)
        columns.append(sqlalchemy.Index(name, *args, **kwargs))
    return columns

#_constraints_ = (
#    ('check', 'x > 3', dict(name='salary_check')), 
#    ('foreignkey', ('a','b'), ('c','d'))
#)
#if hasattr(Cls, '_constraints_') and Cls._constraints_ is not None:
def parse_constraints(constraints):
    columns = list()
    for vals in constraints:
        args, kwargs = get_kwargs(vals)
        columns.append(constraint_lookup[args[0]](*args[1:], **kwargs))

    return columns


def get_kwargs(vals):
    ''' Logic to parse out ordered and keyword arguments.
    '''
    args = vals[:-1] if isinstance(vals[-1], dict) else vals
    kwargs = vals[-1] if isinstance(vals[-1], dict) else dict()
    #print(f'args={args}, kwargs={kwargs}')
    return args, kwargs
