from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd


@dataclasses.dataclass
class SchemaBase:
    
    @classmethod
    def from_schema_definition(cls) -> SchemaBase:
        raise NotImplementedError()
    
    def object_to_dict(self, obj: typing.Any) -> typing.Dict:
        raise NotImplementedError()
    
    def dict_to_object(self, data: typing.Dict[str, typing.Any]) -> typing.Any:
        raise NotImplementedError()
