from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd
import datetime

from .schemabase import SchemaBase

@dataclasses.dataclass
class InferredSchema(SchemaBase):
    columns: typing.List[sqlalchemy.Column]
    indices: typing.List[sqlalchemy.Column]
    constraints: typing.List[sqlalchemy.Column]
    
    @classmethod
    def from_schema_definition(cls, empty_schema: None):
        new_schema: cls = cls(
            columns=None,
            indices = None,
            constraints = None,
        )
        return new_schema
    
    def object_to_dict(self, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return data
    
    def row_to_object(self, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return data
