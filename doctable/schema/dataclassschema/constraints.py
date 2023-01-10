

from ..coltype_map import constraint_lookup

class ConstraintNotFoundError(Exception):
    pass


def Constraint(constraint_type: str, *args, **kwargs):
    '''Return an sqlalchemy constraint.
    Args:
        constraint_type: from doctable.constraint_lookup.keys()
    '''
    try:
        constraint = constraint_lookup[constraint_type]
    except KeyError as e:
        raise ConstraintNotFoundError(f'The name "{constraint_type}" is not a valid constraint. Choose one of {list(constraint_lookup.keys())}')

    return constraint(*args, **kwargs)
    






