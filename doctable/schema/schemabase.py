from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd

from .schemaobject import SchemaObject

@dataclasses.dataclass
class SchemaBase:
    
    @classmethod
    def from_schema_definition(cls) -> SchemaBase:
        raise NotImplementedError()
    
    def object_to_dict(self, obj: SchemaObject) -> typing.Dict:
        raise NotImplementedError()
    
    def dict_to_object(self, obj: SchemaObject) -> typing.Any:
        raise NotImplementedError()
