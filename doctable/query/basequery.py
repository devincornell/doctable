from __future__ import annotations
import sqlalchemy
import dataclasses
import typing

from ..doctable import DocTable
from ..schemas import DocTableSchema

class ObjectIsNotSchemaClass(TypeError):
    pass

@dataclasses.dataclass
class BaseQuery:
    dtab: DocTable

    def execute(self, q, *params) -> sqlalchemy.engine.ResultProxy:
        '''Execute command.'''
        return self.dtab.execute(q, *params)
    
    def col(self, *args, **kwargs) -> sqlalchemy.Column:
        return self.dtab.col(*args, **kwargs)
        
    def _schema_is_obj(self) -> bool:
        return self.dtab._schema_is_obj()

    def _schema_obj_to_dict(self, obj: DocTableSchema) -> typing.Dict[str, typing.Any]:
        '''Convert schema object to a dictionary.'''
        try:    
            return obj._doctable_as_dict()
        except AttributeError as e:
            e2 = ObjectIsNotSchemaClass(f'Object of type {type(obj)} '
                'should be of type DocTableSchema.')
            raise e2 from e
        
    def _dict_to_schema_obj(self, data: typing.Dict[str, typing.Any]) -> DocTableSchema:
        '''Convert dictionary to schema object.'''
        return self.dtab.schema._doctable_from_db(data)
