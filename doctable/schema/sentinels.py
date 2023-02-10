
import enum

# NOTE: This method for making sentinals was borrowed from teh attrs project: attrs.NOTHING

class MissingValueSentinel(enum.Enum):
    MISSING_VALUE = enum.auto()
    def __repr__(self):
        return "MISSING"

MISSING_VALUE = MissingValueSentinel.MISSING_VALUE
'''Used to represent missing data when None is ambiguous.'''



class NothingSentinel(enum.Enum):
    NOTHING = enum.auto()
    def __repr__(self):
        return "NOTHING"

NOTHING = NothingSentinel.NOTHING
'''Used as default when None is ambiguous.'''

