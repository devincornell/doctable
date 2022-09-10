
import functools
import dataclasses

from .errors import *
from .missingvalue import MISSING_VALUE
from .doctableschema import DocTableSchema, colname_to_property, property_to_colname





# I used this formula for the decorator: https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
# outer function used to handle arguments to the decorator
# e.g. @doctable.schema(require_slots=True)

def schema(_Cls=None, *, require_slots: bool = True, enable_accessors: bool = True, **dataclass_kwargs):
    '''A decorator to change a regular class into a schema class.
    '''
    # this is the actual decorator
    def decorator_schema_accessors(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        
        property_names = list()
        for field in dataclasses.fields(Cls):
            property_name = colname_to_property(field.name)#f'_{field.name}'
            property_names.append(property_name)
            
            # dataclasses don't actually create the property unless the default
            # value was a constant, so we just want to replicate that behavior
            # with MISSING_VALUE as the object. Normally it would do that in the 
            # constructor, but we want to create it ahead of time.
            if hasattr(Cls, field.name):
                setattr(Cls, property_name, getattr(Cls, field.name))
            else:
                setattr(Cls, property_name, MISSING_VALUE)
            
            # used a function to generate a class and return the property
            # to solve issue with class definitions in loops
            setattr(Cls, field.name, get_getter_setter(property_name))
            
        # implement new hash function if needed
        if hasattr(Cls, '__hash__'):
            def hashfunc(self):
                return hash(tuple(getattr(self, name) for name in property_names))
            Cls.__hash__ = hashfunc
    
        # add slots
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')
        
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = tuple(property_names)
                    
        return NewClass
    
    # this is the actual decorator
    def decorator_schema_basic(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')

        # add slots
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = tuple([f.name for f in dataclasses.fields(Cls)])
        
        return NewClass

    # in case the user needs to access the old version
    if enable_accessors:
        decorator_schema = decorator_schema_accessors
    else:
        decorator_schema = decorator_schema_basic

    if _Cls is None:
        return decorator_schema
    else:
        return decorator_schema(_Cls)


def get_getter_setter(property_name: str):
    class TmpGetterSetter:
        @property
        def a(self):
            if getattr(self, property_name) is MISSING_VALUE:
                raise DataNotAvailableError(f'The "{property_to_colname(property_name)}" property '
                    'is not available. This might happen if you did not retrieve '
                    'the information from a database or if you did not provide '
                    'a value in the class constructor.')
            
            return getattr(self, property_name)
        
        @a.setter
        def a(self, val):
            setattr(self, property_name, val)
    return TmpGetterSetter.a


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
            __slots__ = tuple([f.name for f in dataclasses.fields(Cls)])
        
        return NewClass

    if _Cls is None:
        return decorator_schema
    else:
        return decorator_schema(_Cls)
    