from __future__ import annotations

import sqlalchemy
import dataclasses
import typing

from ..doctable import DocTable
from ..schemas import DocTableSchema
from .basequery import BaseQuery

class InsertQuery(BaseQuery):
    ############################# Insert Multiple #############################
    def insert_objects(self, schema_objs: typing.List[DocTableSchema], ifnotunique: str = 'fail') -> sqlalchemy.engine.ResultProxy:
        obj_dicts = [self._schema_obj_to_dict(o) for o in schema_objs]
        return self.insert_dicts(obj_dicts, ifnotunique=ifnotunique)
        
    def insert_dicts(self, datum: typing.List[typing.Dict[str, typing.Any]], ifnotunique: str = 'fail') -> sqlalchemy.engine.ResultProxy:
        q = self.query(ifnotunique=ifnotunique)
        return self.execute(q, datum)

    ############################# Insert Single #############################
    def insert_object(self, obj: DocTableSchema, ifnotunique: str = 'fail', **kwargs) -> sqlalchemy.engine.ResultProxy:
        obj_dict = self._schema_obj_to_dict(obj)
        return self.insert_dict(obj_dict, ifnotunique=ifnotunique)

    def insert_dict(self, data: typing.Dict[str, typing.Any], ifnotunique: str = 'fail') -> sqlalchemy.engine.ResultProxy:
        q = self.query(ifnotunique=ifnotunique)
        return self.execute(q, data)

    ############################# Build Actual Query #############################
    def query(self, ifnotunique: str = 'fail') -> sqlalchemy.sql.Insert:
        q: sqlalchemy.sql.Select = sqlalchemy.sql.insert(self.dtab.table)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        return q


    