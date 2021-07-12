

import dataclasses
import functools

class SlotsRequiredError(ValueError):
    message = ('Slots must be enabled by including "__slots__ = []", '
                'Otherwise a slots class cannot be created.')
    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)


# I used this formula for the decorator: https://realpython.com/primer-on-python-decorators/#both-please-but-never-mind-the-bread
# outer function used to handle arguments to the decorator
# e.g. @doctable.row(require_slots=True)
def slots_dataclass(_Cls=None, /, **dataclass_kwargs):
    '''Automattically add slots to the given dataclass.'''

    # this is the actual decorator
    def decorator_slots_dataclass(Cls):
        # creates constructor/other methods using dataclasses
        Cls = dataclasses.dataclass(Cls, **dataclass_kwargs)
        if not hasattr(Cls, '__slots__'):
            raise SlotsRequiredError()

        # add slots
        @functools.wraps(Cls, updated=[])
        class NewClass(Cls):
            __slots__ = [f.name for f in dataclasses.fields(Cls)]
        
        return NewClass

    if _Cls is None:
        return decorator_slots_dataclass
    else:
        return decorator_slots_dataclass(_Cls)