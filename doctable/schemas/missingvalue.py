
#import dataclasses

#@dataclasses.dataclass(frozen=True, eq=True)
class MissingType:
    ''' Represents value that was not retrieved from select statement.
    '''
    pass
MISSING_VALUE = MissingType()
