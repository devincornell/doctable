from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd

from .errors import RowToObjectConversionFailedError, ObjectToDictCovnersionFailedError
from ..schemas import DocTableSchema

class SchemaBase:
    schema_class: type[DocTableSchema]


    def object_to_dict_interface(self, obj: typing.Any) -> DocTableSchema:
        try:
            return self.object_to_dict(obj)
        except BaseException as e:
            raise ObjectToDictCovnersionFailedError(f'Conversion from {type(obj)} to dict '
                f'failed upon retrieval from database. If expected return data does not '
                f'match the schema object type, try using .q.select_raw(), or some variant thereof.') from e

    def row_to_object_interface(self, data: sqlalchemy.engine.row.LegacyRow) -> DocTableSchema:
        try:
            return self.row_to_object(data)
        except BaseException as e:
            raise RowToObjectConversionFailedError(f'Conversion from {type(data)} to {self.schema_class} '
                f'failed. This may be caused by inserting objects of innapropriate type into the db.') from e


    @classmethod
    def from_schema_definition(cls) -> SchemaBase:
        raise NotImplementedError()
    
    def object_to_dict(self, obj: typing.Any) -> typing.Dict:
        raise NotImplementedError()
    
    def row_to_object(self, data: sqlalchemy.engine.row.LegacyRow) -> typing.Any:
        raise NotImplementedError()
