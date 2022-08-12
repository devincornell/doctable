
import functools
import dataclasses

from .errors import *
from .emptyvalue import EmptyValue
from .doctableschema import DocTableSchema





# I used this formula for the decorator: https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
# outer function used to handle arguments to the decorator
# e.g. @doctable.schema(require_slots=True)



def get_getter_setter(property_name: str):
    class TmpGetterSetter:
        @property
        def a(self):
            if getattr(self, property_name) is dataclasses._MISSING_TYPE:
                raise ValueNotRetrievedEror(f'The "{property_name[1:]}" property '
                    'was never retrieved from the database. This might appear if '
                    'you specified columns in your SELECT statement.')
            return getattr(self, property_name)
        
        @a.setter
        def a(self, val):
            setattr(self, property_name, val)
    return TmpGetterSetter.a


def schema(_Cls=None, *, require_slots=True, **dataclass_kwargs):

    # this is the actual decorator
    def decorator_schema(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        
        slot_var_names = list()
        for field in dataclasses.fields(Cls):
            property_name = f'_{field.name}'
            
            # dataclasses don't actually create the property unless the default
            # value was a constant, so we just want to replicate that behavior
            # with EmptyValue as the object. Normally it would do that in the 
            # constructor, but we want to create it ahead of time.
            if hasattr(Cls, field.name):
                setattr(Cls, property_name, getattr(Cls, field.name))
            else:
                setattr(Cls, property_name, EmptyValue())
            
            # used a function to generate a class and return the property
            # to solve issue with class definitions in loops
            setattr(Cls, field.name, get_getter_setter(property_name))
    
        # add slots
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')
        
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = [f.name for f in dataclasses.fields(Cls)]
        
        return NewClass

    if _Cls is None:
        return decorator_schema
    else:
        return decorator_schema(_Cls)

def schema_depric(_Cls=None, *, require_slots=True, **dataclass_kwargs):

    # this is the actual decorator
    def decorator_schema(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')

        # add slots
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = [f.name for f in dataclasses.fields(Cls)]
        
        return NewClass

    if _Cls is None:
        return decorator_schema
    else:
        return decorator_schema(_Cls)
    