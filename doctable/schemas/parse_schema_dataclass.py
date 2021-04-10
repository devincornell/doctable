
import datetime
import sqlalchemy as sa
from dataclasses import dataclass, field, fields
from .coltype_map import python_to_slqlchemy_type, string_to_sqlalchemy_type, constraint_lookup



def parse_schema_dataclass(dclass):
    ''' Convert a dataclass definition to a list of sqlalchemy columns.
    '''
    columns = list()
    
    # regular data columns (uses dataclass features)
    for f in fields(dclass):
        if f.init:
            if 'coltype' in f.metadata: # specified type using string
                use_type = string_to_sqlalchemy_type[f.metadata['coltype']]
                del f.metadata['coltype']
            
            else: # infer column type based on python datatype hints
                use_type = python_to_slqlchemy_type.get(f.type, sa.PickleType)
            
            col = sa.Column(f.name, use_type, **f.metadata)
            columns.append(col)

    #_indices_ = {
    #    'my_index': ('c1', 'c2', {'unique':True}),
    #    'other_index': ('c1',),
    #}
    if hasattr(dclass, '_indices_') and dclass._indices_ is not None:
        for name, vals in dclass._indices_.items():
            args, kwargs = get_kwargs(vals)
            columns.append(sa.Index(name, *args, **kwargs))

    #_constraints_ = (
    #    ('check', 'x > 3', dict(name='salary_check')), 
    #    ('foreignkey', ('a','b'), ('c','d'))
    #)
    if hasattr(dclass, '_constraints_') and dclass._constraints_ is not None:
        for vals in dclass._constraints_:
            args, kwargs = get_kwargs(vals)
            columns.append(constraint_lookup[args[0]](*args[1:], **kwargs))

    return columns

def get_kwargs(vals):
    args = vals[:-1] if isinstance(vals[-1], dict) else vals
    kwargs = vals[-1] if isinstance(vals[-1], dict) else dict()
    #print(f'args={args}, kwargs={kwargs}')
    return args, kwargs
