from __future__ import annotations

import sqlalchemy
import dataclasses
import typing
import pandas as pd
import datetime

from .schemabase import SchemaBase
from .columnmetadata import ColumnMetadata
from .schemaobject import SchemaClass
from ..schemas import string_to_sqlalchemy_type
from ..util import is_sequence

@dataclasses.dataclass
class StringSchema(SchemaBase):
    columns: typing.List[sqlalchemy.Column]

    @classmethod
    def from_schema_definition(cls, schema_obj: typing.List[typing.Tuple], default_fpath = './'):
        new_schema: cls = cls(
            columns = cls.parse_schema_strings(schema_obj, default_fpath=default_fpath)
        )
        return new_schema
    
    def object_to_dict(self, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return data
    
    def dict_to_object(self, data: typing.Dict[str, typing.Any]) -> typing.Dict[str, typing.Any]:
        return data

    @classmethod
    def parse_schema_strings(cls, schema, default_fpath='./'):
        columns = list()
        for colinfo in schema:
            n = len(colinfo)
            if n not in (2,3,4):
                raise ValueError('A schema entry must have 2+ arguments: (type,name,..)')
            
            # column is regular type
            if colinfo[0] in string_to_sqlalchemy_type:
                coltype, colname = colinfo[:2]
                colargs = colinfo[2] if n > 2 else dict()
                coltypeargs = colinfo[3] if n > 3 else dict()
                if coltype in ('picklefile','textfile','jsonfile') and 'fpath' not in coltypeargs:
                    coltypeargs['fpath'] = default_fpath+'_'+colname
                
                col = sqlalchemy.Column(colname, string_to_sqlalchemy_type[coltype](**coltypeargs), **colargs)
                columns.append(col)
            else:
                if colinfo[0] == 'idcol': #shortcut for typical id integer primary key etc
                    col = sqlalchemy.Column(colinfo[1], sqlalchemy.Integer, primary_key=True, autoincrement=True)
                    columns.append(col)
                elif colinfo[0] == 'date_added': #shortcut for typical id integer primary key etc
                    col = sqlalchemy.Column(colinfo[1], sqlalchemy.DateTime, default=datetime.datetime.now)
                    columns.append(col)
                elif colinfo[0] == 'date_updated': #shortcut for typical id integer primary key etc
                    col = sqlalchemy.Column(colinfo[1], sqlalchemy.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
                    columns.append(col)
                elif colinfo[0] == 'index':
                    # ('index', 'ind0', ('name','address'),dict(unique=True)),
                    indargs = colinfo[2] if n > 2 else dict()
                    indkwargs = colinfo[3] if n > 3 else dict()
                    ind = sqlalchemy.Index(colinfo[1], *indargs, **indkwargs)
                    columns.append(ind)
                elif colinfo[0] == 'check_constraint':
                    # ('check_constraint','age >= 0 AND age < 120',, dict(name='age')),
                    kwargs = colinfo[2] if n > 2 else dict()
                    const = sqlalchemy.CheckConstraint(colinfo[1], **kwargs)
                    columns.append(const)
                elif colinfo[0] == 'unique_constraint':
                    # ('unique_constraint', ('name','address'), dict(name='name_addr')),
                    kwargs = colinfo[2] if n > 2 else dict()
                    const = sqlalchemy.UniqueConstraint(*colinfo[1], **kwargs)
                    columns.append(const)
                elif colinfo[0] == 'primarykey_constraint':
                    # ('primarykey_constraint', ('name','address'),dict(unique=True)),
                    kwargs = colinfo[2] if n > 2 else dict()
                    const = sqlalchemy.PrimaryKeyConstraint(*colinfo[1], **kwargs)
                    columns.append(const)
                elif colinfo[0] == 'foreignkey':
                    if n < 3:
                        raise ValueError('A foreignkey constraint should follow the form '
                                '(\'foreignkey\', from_col(s), to_col(s), **kwargs).')
                    
                    fro = colinfo[1] if is_sequence(colinfo[1]) else [colinfo[1]]
                    to = colinfo[2] if is_sequence(colinfo[2]) else [colinfo[2]]
                    kwargs = colinfo[3] if n > 3 else dict()
                    const = sqlalchemy.ForeignKeyConstraint(fro, to, **kwargs)
                    columns.append(const)
                else:
                    raise ValueError('Column or constraint type "{}" was not recognized.'
                                    ''.format(colinfo[0]))
                
        return columns

        