from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

from .fieldargs import FieldArgs
from .columnargs import ColumnArgs

def Column(
    column_args: typing.Optional[ColumnArgs] = None,
    field_args: typing.Optional[FieldArgs] = None,
) -> dataclasses.field:
    '''Record column information in the metadata of a dataclass field.'''
    field_args = field_args if field_args is not None else FieldArgs()
    column_args = column_args if column_args is not None else ColumnArgs()

    # NOTE: this is all old code
    # bind column args to metadata
    #metadata = {
    #    **field_args.metadata, 
    #    COLUMN_METADATA_ATTRIBUTE_NAME: column_args,
    #}
    # replaces above (consistent with the getter/setter pattern)
    #metadata = dict(field_args.metadata) if field_args.metadata is not None else dict()
    #set_column_args(metadata, column_args)
    #
    #fields_without_metadata = field_args.dict_without_metadata()
    #try:
    #    return dataclasses.field(metadata=metadata, **fields_without_metadata)
    #except TypeError as e:
    #    del fields_without_metadata['kw_only']
    #    return dataclasses.field(metadata=metadata, **fields_without_metadata)
    return field_args.get_dataclass_field(column_args)


