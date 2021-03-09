
class EmptyValue:
    ''' Represents value that was not retrieved from select statement.
    '''
    @property
    def val(self):
        return None
    
    def __repr__(self):
        return self.__class__.__name__
