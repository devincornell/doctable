
import functools
import dataclasses
import typing

from .errors import RowDataNotAvailableError, SlotsRequiredError
from .missingvalue import MISSING_VALUE
from .doctableschema import DocTableSchema
from .operators import set_attr_map, get_attr_map, property_to_attr, attr_to_property, attr_value_tuples, asdict, asdict_ignore_missing

# I used this formula for the decorator: https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
# outer function used to handle arguments to the decorator
# e.g. @doctable.schema(require_slots=True)

def schema(
        _Cls: type = None, *, 
        require_slots: bool = True, 
        enable_properties: bool = True, 
        **dataclass_kwargs
    ) -> type:
    '''A decorator to change a regular class into a schema object class.
    '''
    # in case the user needs to access the old version
    if enable_properties:
        decorator_schema = schema_decorator_properties_factory(
            require_slots=require_slots, 
            dataclass_kwargs=dataclass_kwargs
        )
    else:
        decorator_schema = schema_decorator_basic_factory(
            require_slots=require_slots, 
            dataclass_kwargs=dataclass_kwargs
        )

    if _Cls is None:
        return decorator_schema
    else:
        return decorator_schema(_Cls)

def schema_decorator_properties_factory(
        require_slots: bool, 
        dataclass_kwargs: typing.Dict[str, typing.Any]
    ) -> typing.Callable[[type], type]:

    # this is the actual decorator
    def schema_decorator_with_properties(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')
        
        attr_map = dict()
        for field in dataclasses.fields(Cls):
            attr_name = property_to_attr(field.name)#f'_{field.name}'            
            attr_map[field.name] = attr_name
            
            # dataclasses don't actually create the property unless the default
            # value was a constant, so we just want to replicate that behavior
            # with MISSING_VALUE as the object. Normally it would do that in the 
            # constructor, but we want to create it ahead of time.
            if hasattr(Cls, field.name):
                setattr(Cls, attr_name, getattr(Cls, field.name))
            else:
                setattr(Cls, attr_name, MISSING_VALUE)
            
            # used a function to generate a class and return the property
            # to solve issue with class definitions in loops
            setattr(Cls, field.name, get_getter_setter(attr_name))
        
        # set map from properties to attributes
        set_attr_map(Cls, attr_map)
                
        # implement new hash function if needed
        if hasattr(Cls, '__hash__'):
            def hashfunc(self):
                return hash(tuple(v for pn,an,v in attr_value_tuples(Cls)))
            Cls.__hash__ = hashfunc
        
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = tuple(an for pn,an,v in attr_value_tuples(Cls))
            
        return NewClass
    
    return schema_decorator_with_properties



def schema_decorator_basic_factory(
        require_slots: bool, 
        dataclass_kwargs: typing.Dict[str, typing.Any]
    ) -> typing.Callable[[type], type]:
    
    # this is the actual decorator
    def schema_decorator_basic(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        
        # check for slots
        if require_slots and not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError('Slots must be enabled by including "__slots__ = []". '
                'Otherwise set doctable.schema(require_slots=False).')

        # the attr_name field will be used to access attributes
        set_attr_map(Cls, {f.name:f.name for f in dataclasses.fields(Cls)})
        
        # add slots
        @functools.wraps(Cls, updated=[])
        class NewClass(DocTableSchema, Cls):
            __slots__ = tuple([f.name for f in dataclasses.fields(Cls)])
        
        return NewClass
    
    return schema_decorator_basic






def get_getter_setter(property_name: str):
    class TmpGetterSetter:
        @property
        def a(self):
            if getattr(self, property_name) is MISSING_VALUE:
                colname = attr_to_property(property_name)
                raise RowDataNotAvailableError(f'The "{colname}" property '
                    'is not available. This might happen if you did not retrieve '
                    'the information from a database or if you did not provide '
                    'a value in the class constructor.')
            
            return getattr(self, property_name)
        
        @a.setter
        def a(self, val):
            setattr(self, property_name, val)
    return TmpGetterSetter.a







