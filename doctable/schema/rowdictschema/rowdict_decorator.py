from __future__ import annotations

import typing
import attrs
import functools
import warnings
import sqlalchemy

from ..dataclassschema import RowDataNotAvailableError, SlotsRequiredError
from ..sentinels import NOTHING
from .schemaobject import SchemaObject
from .operators import set_rowdict, set_rowdict_attr, get_rowdict_attr, rowdict_obj_from_dict, has_rowdict, rowdict_attr_name


def schema_experimental(
        _Cls: type = None, 
        **attrs_kwargs,
    ) -> type:
    '''A decorator to change a regular class into a schema object class.
    '''
    # in case the user needs to access the old version
    rowdict_decorator = rowdict_decorator_factory(
        attrs_kwargs=attrs_kwargs
    )

    if _Cls is None:
        return rowdict_decorator
    else:
        return rowdict_decorator(_Cls)



def rowdict_decorator_factory(
        attrs_kwargs: typing.Dict[str, typing.Any],
    ) -> typing.Callable[[type], type]:

    # this is the actual decorator
    def rowdict_decorator(Cls):
        # creates constructor/other methods using attrs
        # turn off slots because we don't need them
        Cls = attrs.define(**{'slots': False, **attrs_kwargs})(Cls)
                
        # will overload each field with a getter and setter that secretly
        # actually just edits the underlying rowdict object
        for field in attrs.fields(Cls):
            getter_setter = get_getter_setter_rowdict(field.name)
            #print(f'{field.name=}, {getter_setter=}')
            setattr(Cls, field.name, getter_setter)
            #print(getattr(Cls, field.name))
        
        # NOTE: I'll have to look into making equivalents to these. Does attrs do this?
        # implement new hash function if needed
        #if hasattr(Cls, '__hash__'):
        #    def hashfunc(self):
        #        return hash(as_value_tuple(self))
        #    Cls.__hash__ = hashfunc
            
        #def binary_compare_factory(attrname: str):
        #    def binary_compare(self: Cls, other: Cls):
        #        return getattr(as_value_tuple(self), attrname)(as_value_tuple(other))
        #
        #if hasattr(Cls, '__eq__'): Cls.__eq__ = binary_compare_factory('__eq__')
        #if hasattr(Cls, '__lt__'): Cls.__lt__ = binary_compare_factory('__lt__')
        #if hasattr(Cls, '__le__'): Cls.__le__ = binary_compare_factory('__le__')
        #if hasattr(Cls, '__gt__'): Cls.__gt__ = binary_compare_factory('__gt__')
        #if hasattr(Cls, '__ge__'): Cls.__ge__ = binary_compare_factory('__ge__')
        
        #NOTE: IN FUTURE, RAISE WARNING IF Cls OVERWRITES SchemaObject METHODS
        @functools.wraps(Cls, updated=[])
        class NewClass(SchemaObject, Cls):
            # NOTE: will this work to add slots? not sure - need to test it
            __slots__ = [rowdict_attr_name]
            def __init__(self, *args, _doctable_from_row_obj: typing.Dict = None, **kwargs):
                '''Setting __doctable_rowdict allows user to bypass arguments entirely.'''
                if _doctable_from_row_obj is not None:
                    _doctable_from_row_obj = dict(_doctable_from_row_obj)
                    set_rowdict(self, _doctable_from_row_obj)
                else:
                    set_rowdict(self, dict())
                    Cls.__init__(self, *args, **kwargs)
                    #super(Cls, self).__init__(*args, **kwargs) # idk why this didn't work
            
            @classmethod
            def _doctable_from_row_obj(cls, row: typing.Dict) -> NewClass:
                '''Used to construct this object from result of an sql query.'''
                return rowdict_obj_from_dict(cls, row)
                
        return NewClass
    
    return rowdict_decorator


def get_getter_setter_rowdict(property_name: str):
    '''Returns a new getter/setter method that simply edits an underlying dict.'''
    class TmpGetterSetter:

        @property
        def a(self):
            try:
                return get_rowdict_attr(self, property_name)
            except KeyError:
                raise RowDataNotAvailableError(f'The "{property_name}" property '
                    'is not available. This might happen if you did not retrieve '
                    'the information from a database or if you did not provide '
                    'a value in the class constructor.')            

        @a.setter
        def a(self, val: typing.Any):
            if val is not NOTHING:
                set_rowdict_attr(self, property_name, val)
    
    return TmpGetterSetter.a











