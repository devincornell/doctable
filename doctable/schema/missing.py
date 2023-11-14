import enum

class MissingType(enum.Enum):
    MISSING = enum.auto()
    def __repr__(self):
        return "MISSING"

MISSING = MissingType.MISSING
'''Represents value that should not be inserted into the database or was not retreived from the database.'''


