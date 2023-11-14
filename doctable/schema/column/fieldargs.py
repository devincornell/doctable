from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

from .columnargs import ColumnArgs, set_column_args
from ..missing import MISSING, MissingType


@dataclasses.dataclass
class FieldArgs:
    '''Creates kwargs dict to be passed to dataclasses.field. Read about args here:
        https://docs.python.org/3/library/dataclasses.html
    '''
    default: typing.Any = MISSING # dataclass.field: default value for column
    default_factory: typing.Union[typing.Callable[[], typing.Any], MissingType] = MISSING # default factory for column
    init_required: bool = False # will set default and default_factory to MISSING if True
    repr: bool = True # dataclass.field: whether to include in repr
    hash: typing.Optional[bool] = None # dataclass.field: whether to include in hash
    init: bool = True # dataclass.field: whether to include in init
    compare: bool = True # dataclass.field: whether to include in comparison
    kw_only: typing.Union[bool, MissingType] = MISSING # dataclass.field: whether to include in kw_only
    metadata: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict) # dataclass.field: metadata to include in field
    
    def get_dataclass_field(self, column_args: ColumnArgs) -> dataclasses.Field:
        metadata = dict(self.metadata) #if field_args.metadata is not None else dict()
        set_column_args(metadata, column_args)
        
        fields_without_metadata = self.dict_without_metadata()
        try:
            return dataclasses.field(metadata=metadata, **fields_without_metadata)
        except TypeError as e:
            del fields_without_metadata['kw_only']
            return dataclasses.field(metadata=metadata, **fields_without_metadata)

    def dict_without_metadata(self) -> typing.Dict[str, typing.Any]:
        v = dataclasses.asdict(self)
        del v['metadata']

        # this is a way to wipe default and default factory        
        del v['init_required']
        if self.init_required:
            v['default'] = dataclasses.MISSING
            v['default_factory'] = dataclasses.MISSING
        
        # this is a hack to get around the fact that this dataclass uses the same
        # default value that the dataclasses.field argument does (dataclasses.MISSING)
        # this is the best way I could think of
        if self.default_factory is MISSING:
            v['default_factory'] = dataclasses.MISSING
        else:
            v['default'] = dataclasses.MISSING
            
        if self.kw_only is MISSING:
            v['kw_only'] = dataclasses.MISSING
        
        return v



