from __future__ import annotations

import sqlalchemy
import dataclasses
import typing

from ..doctable import DocTable
from ..schemas import DocTableSchema
from .basequery import BaseQuery

class DeleteQuery(BaseQuery):
    ############################# Insert Multiple #############################

    ############################# Build Actual Query #############################
    def query(self, ifnotunique: str = 'fail') -> sqlalchemy.sql.Insert:
        q: sqlalchemy.sql.Select = sqlalchemy.sql.insert(self.dtab.table)
        q = q.prefix_with('OR {}'.format(ifnotunique.upper()))
        return q


    