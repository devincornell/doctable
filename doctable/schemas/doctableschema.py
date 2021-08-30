
import dataclasses
from .emptyvalue import EmptyValue

miss_col_message = 'The column "{name}" was not retreived in the select statement.'

class DocTableSchema:
    ''' Base class for column objects.
    '''
    __slots__ = [] # for inheriting class
    def _uses_slots(self):
        ''' Check if this class uses slots.
        '''
        return not hasattr(self, '__dict__')

    ########################## Basic Accessors ##########################
    def __getitem__(self, attr):
        ''' Access data, throwing error when accessing element that was not
                retrieved from the database.
        '''
        val = getattr(self, attr)#self.__dict__[attr]
        if isinstance(val, EmptyValue):
            raise KeyError(miss_col_message.format(name=attr))
        return val
    
    def get(self, attr):
        ''' Access data without throwing an error when accessing element.
        '''
        return getattr(self, attr)
    
    def __repr__(self):
        '''Hides cols with values of type EmptyValue.
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
        '''Convert to dictionary, ignoring EmptyValue objects.
        '''
        if hasattr(self, '__dict__'):
            return {k:v for k,v in self.__dict__.items() if not isinstance(v, EmptyValue)}
        else:
            return {name:getattr(self, name) for name in self.__slots__ 
                                if not isinstance(getattr(self, name), EmptyValue)}
