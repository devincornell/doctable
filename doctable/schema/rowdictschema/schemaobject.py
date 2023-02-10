
from .operators import rowdict_has_attr, get_rowdict_attr, get_rowdict, get_rowdict_attr_default, set_rowdict
from ..sentinels import NOTHING
import typing

class SchemaObject:
    '''Base class of a schema object, inherited in the decorator.
        As well as defining an object type for type hints later,
            this method also provides some convenience methods.
    '''

    ################## Dunder ##################
    def __repr__(self):
        '''Shows data from dictionary.
        '''
        vals = ', '.join([f'{k}={v}' for k,v in get_rowdict(self).items() if v != NOTHING])
        return f'{self.__class__.__name__}({vals})'

    def __getitem__(self, attr):
        ''' Access data, throwing error when accessing element that was not
                retrieved from the database.
        '''
        return get_rowdict_attr(self, attr)

    ################## Access Data in Different Way ##################
    def v(self) -> typing.Dict:
        '''Get property, bypassing error if property doesn't exist.'''
        return get_rowdict(self)

    def get_val(self, name: str) -> typing.Any:
        return get_rowdict_attr(self, name)

    def get_val_default(self, name: str, default: typing.Any) -> typing.Any:
        return get_rowdict_attr_default(self, name, default)

    ################## Type Conversion ##################

    def asdict(self) -> typing.Dict:
        return dict(get_rowdict(self))

    def astuple(self) -> typing.Tuple:
        return tuple(get_rowdict(self).items())

    def attr_is_available(self, name: str) -> bool:
        return rowdict_has_attr(self, name)



