from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

from ..missing import MISSING





@dataclasses.dataclass
class FieldArgs:
    '''Creates kwargs dict to be passed to dataclasses.field. Read about args here:
        https://docs.python.org/3/library/dataclasses.html
    '''
    default: typing.Any = MISSING # dataclass.field: default value for column
    default_factory: typing.Optional[typing.Callable[[], typing.Any]] = MISSING # default factory for column
    repr: bool = True # dataclass.field: whether to include in repr
    hash: bool = None # dataclass.field: whether to include in hash
    init: bool = True # dataclass.field: whether to include in init
    compare: bool = True # dataclass.field: whether to include in comparison
    kw_only: bool = MISSING # dataclass.field: whether to include in kw_only
    metadata: typing.Optional[typing.Dict[str, typing.Any]] = dataclasses.field(default_factory=dict) # dataclass.field: metadata to include in field

    def dict_without_metadata(self) -> typing.Dict[str, typing.Any]:
        v = dataclasses.asdict(self)
        del v['metadata']

        # this is a hack to get around the fact that this dataclass uses the same
        # default value that the dataclasses.field argument does (dataclasses.MISSING)
        # this is the best way I could think of
        if self.default_factory is MISSING:
            v['default_factory'] = dataclasses.MISSING
        return v



