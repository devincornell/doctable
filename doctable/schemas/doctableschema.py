
import dataclasses
from .emptyvalue import EmptyValue

class DocTableSchema:
    ''' Base class for column objects.
    '''
    miss_col_message = 'The column "{name}" was not retreived in the select statement.'

    ########################## Basic Accessors ##########################
    def __getitem__(self, attr):
        ''' Access data, throwing error when accessing element that was not
                retrieved from the database.
        '''
        val = self.__dict__[attr]
        if isinstance(val, EmptyValue):
            raise KeyError(self.miss_col_message.format(name=attr))
        return val
    
    @property
    def v(self):
        ''' Access data without throwing an error when accessing element.
        '''
        return self.__dict__
    
    def __repr__(self):
        cn = ", ".join([(f'{k}=\'{v}\'' if isinstance(v,str) else f'{k}={v}') 
            for k,v in self._doctable_as_dict().items()])
        return f'{self.__class__.__name__}({cn})'
    
    ########################## Conversions ##########################
    def _doctable_as_dict(self):
        ''' Convert to dictionary, ignoring EmptyValue objects.
        '''
        return {k:v for k,v in self.__dict__.items() if not isinstance(v, EmptyValue)}
