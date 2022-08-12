
#import dataclasses

#@dataclasses.dataclass(frozen=True, eq=True)
class MissingValue:
    ''' Represents value that was not retrieved from select statement.
    '''
    pass
