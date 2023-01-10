from __future__ import annotations
import typing

if typing.TYPE_CHECKING:
    from ..doctable import DocTable


import sqlalchemy
import dataclasses
import typing
import pandas as pd



from ..schema import DocTableSchema
from ..util import is_sequence

from .selectqueryargs import SelectQueryArgs
from .errors import *

typing.Literal['FAIL', 'IGNORE', 'REPLACE']


from .querybase import QueryBase, SingleColumn, ColumnList


class InsertQuery(QueryBase):

    dtab: DocTable
    ######################################## High-level inserts that infer type. ########################################

    ######################################## Insert Multiple ########################################
    def insert_multi(self, 
            schema_objs: ColumnList, 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
            **kwargs
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert multiple rows as objects into the db.'''
        if not is_sequence(schema_objs):
            raise TypeError('insert_multi and insert_multi_raw accept a list or '
            f'tuple of schema objects to insert.')
        obj_dicts = [self.dtab.schema.object_to_dict_interface(o) for o in schema_objs]
        return self.insert_multi_raw(obj_dicts, ifnotunique=ifnotunique, **kwargs)
        
    def insert_multi_raw(self, 
            datum: typing.List[typing.Dict[str, typing.Any]], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
            **kwargs
        ) -> sqlalchemy.engine.ResultProxy:
        '''Insert multiple rows as dictionaries into the db.'''
        if not is_sequence(datum):
            raise TypeError('insert_multi and insert_multi_raw accept a list or '
            f'tuple of schema objects to insert.')
        q = self.insert_query(ifnotunique=ifnotunique)
        return self.dtab.execute(q, datum, **kwargs)

    ######################################## Insert Single ########################################
    def insert_single(self, 
            obj: DocTableSchema, 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail', 
            **kwargs
        ) -> sqlalchemy.engine.ResultProxy:
        if is_sequence(obj):
            raise TypeError(f'Provided object must not be a sequence. If you '
                f'intended to insert multiple objects, use .q.insert_multi()')
        obj_dict = self.dtab.schema.object_to_dict_interface(obj)
        return self.insert_single_raw(obj_dict, ifnotunique=ifnotunique, **kwargs)

    def insert_single_raw(self, 
            data: typing.Dict[str, typing.Any], 
            ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail',
            **kwargs
        ) -> sqlalchemy.engine.ResultProxy:
        if is_sequence(data):
            raise TypeError('insert_single and insert_single_raw accept a '
            f'single schema object for insertion.')
        q = self.insert_query(ifnotunique=ifnotunique)
        return self.dtab.execute(q, data, **kwargs)

    ######################################## Build Insert Query ########################################
    def insert_query(self, ifnotunique: typing.Literal['FAIL', 'IGNORE', 'REPLACE'] = 'fail') -> sqlalchemy.sql.Insert:
        self._check_readonly('insert')
        q: sqlalchemy.sql.Select = sqlalchemy.sql.insert(self.dtab.table)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        return q


