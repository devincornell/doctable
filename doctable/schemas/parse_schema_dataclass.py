
import datetime
import sqlalchemy as sa
from dataclasses import dataclass, field, fields
from .coltype_map import python_to_slqlchemy_type, string_to_sqlalchemy_type, constraint_lookup



def parse_schema_dataclass(Cls, indices: dict, constraints: list):
    ''' Convert a dataclass definition to a list of sqlalchemy columns.
    '''
    return parse_columns(Cls) + parse_indices(indices) + parse_constraints(constraints)


def parse_columns(Cls):
    ''' Convert the dataclass member variables to sqlalchemy columns.
    '''
    columns = list()
    for f in fields(Cls):
        if f.init:
            metadata = f.metadata.copy()
            if 'coltype' in metadata: # specified type using string
                use_type = string_to_sqlalchemy_type[metadata['coltype']]
                del metadata['coltype']
            
            else: # infer column type based on python datatype hints
                use_type = python_to_slqlchemy_type.get(f.type, sa.PickleType)

            if 'type_args' in metadata:
                use_type = use_type(**metadata['type_args'])
                del metadata['type_args']
            
            col = sa.Column(f.name, use_type, **metadata)
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
        columns.append(sa.Index(name, *args, **kwargs))
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
