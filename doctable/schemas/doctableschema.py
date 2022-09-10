
import dataclasses
from .missingvalue import MISSING_VALUE

miss_col_message = 'The column "{name}" was not retreived in the select statement.'


def colname_to_property(colname: str) -> str:
    return f'_doctable__{colname}'

def property_to_colname(property: str) -> str:
    return '__'.join(property.split('__')[1:])

class DocTableSchema:
    ''' Base class for column objects.
    '''
    __slots__ = [] # for inheriting class
    #def _uses_slots(self):
    #    ''' Check if this class uses slots.
    #    '''
    #    return hasattr(self, '__slots__')

    ########################## Basic Accessors ##########################
    #def __getitem__(self, attr):
    #    ''' Access data, throwing error when accessing element that was not
    #            retrieved from the database.
    #    '''
    #    val = getattr(self, attr)#self.__dict__[attr]
    #    if val is MISSING_VALUE:
    #        raise KeyError(miss_col_message.format(name=attr))
    #    return val
    
    def get_val(self, colname):
        ''' Access data related to the property.
        '''
        return getattr(self, colname_to_property(colname))
    
    def __repr__(self):
        '''Hides cols with values of type MISSING_VALUE.
        '''
        cn = ", ".join([(f'{k}=\'{v}\'' if isinstance(v,str) else f'{k}={v}') 
            for k,v in self._doctable_as_dict().items()])
        return f'{self.__class__.__name__}({cn})'
    
    ########################## Conversions ##########################
    
    def as_dict(self, *args, **kwargs):
        '''Public interface for _doctable_as_dict().
        '''
        return self._doctable_as_dict(*args, **kwargs)

    def _doctable_as_dict(self):
        '''Convert to dictionary, ignoring MISSING_VALUE objects.
        '''
        #attrs = dict()
        #if hasattr(self, '__dict__'):
        #    attrs = {**attrs, **{k:v for k,v in self.__dict__.items() if v is not MISSING_VALUE}}
        #
        #if hasattr(self, '__slots__'):
        #    attrs = {**attrs, **{name:getattr(self, name) for name in self.__slots__ 
        #                        if getattr(self, name) is not MISSING_VALUE}}
        #return attrs
        # will be slightly different depending on schema decorator being used
        try:
            return {f.name:getattr(self,f.name) for f in dataclasses.fields(self) 
                                        if self.get_val(f.name) is not MISSING_VALUE}
        except AttributeError:
            return {f.name:getattr(self,f.name) for f in dataclasses.fields(self) 
                                        if getattr(self,f.name) is not MISSING_VALUE}

    @classmethod
    def _doctable_from_db(cls, **col_values):
        '''DocTable uses this as a constructor to fill missing values with MISSING_VALUE objects.
        '''
        return cls(**{f.name:col_values.get(f.name,MISSING_VALUE) for f in dataclasses.fields(cls)})
    
    
