from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

METADATA_ATTRIBUTE_NAME = '_column_args'

# https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Text
type_hint_to_column_type = {
    int: sqlalchemy.Integer,
    str: sqlalchemy.String,
    float: sqlalchemy.Float,
    bool: sqlalchemy.Boolean,
    datetime.datetime: sqlalchemy.DateTime,
    datetime.time: sqlalchemy.Time,
    datetime.date: sqlalchemy.Date,
    bytes: sqlalchemy.LargeBinary,
    typing.Any: sqlalchemy.PickleType,
}

@dataclasses.dataclass
class ColumnParams:
    column_name: str
    sqlalchemy_type: sqlalchemy.TypeClause
    foreign_key: str
    type_kwargs: typing.Dict[str, typing.Any]
    dataclass_field: typing.Dict[str, typing.Any]
    column_kwargs: typing.Dict[str, typing.Any]

    @classmethod
    def empty(cls) -> ColumnParams:
        return cls(
            column_name=None,
            sqlalchemy_type=None,
            foreign_key=None,
            type_kwargs=None,
            dataclass_field=None,
            column_kwargs=None,
        )

def column(
    column_name: str = None, # name of the column in the database
    sqlalchemy_type: sqlalchemy.TypeClause = None, # type of column in database using sqlachemy types
    foreign_key: str = None, # name of the column (tabname.colname) that this column references
    type_kwargs: typing.Dict[str, typing.Any] = None, # keyword arguments to pass to sqlalchemy type
    dataclass_field: typing.Dict[str, typing.Any] = None, # keyword arguments to pass to dataclass.field
    **column_kwargs # pass to sqlalchemy.Column. ex: primary_key=True, nullable=True, etc.
) -> dataclasses.field:
    '''Get column info from only a sqlalchemy type.'''
    return dataclasses.field(
        metadata={
            **dataclass_field.get('metadata', {}), 
            METADATA_ATTRIBUTE_NAME: ColumnParams(
                column_name=column_name,
                sqlalchemy_type=sqlalchemy_type,
                foreign_key=foreign_key,
                type_kwargs=type_kwargs,
                dataclass_field=dataclass_field,
                column_kwargs=column_kwargs,
            ),
        },
        **dataclass_field
    )

@dataclasses.dataclass
class ColumnInfo:
    attr_name: str # name of attribute in data container
    type_hint: type
    params: ColumnParams

    @classmethod
    def empty(cls, name: str, type_hint: type) -> ColumnInfo:
        return cls(
            attr_name=name,
            type_hint=type_hint,
            params=ColumnParams.empty(),
        )

    @classmethod
    def from_sqlalchemy(cls, dtype: sqlalchemy.TypeClause, **column_kwargs) -> ColumnInfo:
        '''Get column info from only a sqlalchemy type.'''
        return cls(
            dtype=dtype,
            dtype_args=(),
            dtype_kwargs={},
            column_kwargs=column_kwargs,
        )

    @classmethod
    def from_field(cls, field: dataclasses.Field) -> ColumnInfo:
        '''Get column info from a dataclass field.'''
        try:
            params = field.metadata[METADATA_ATTRIBUTE_NAME]
        except KeyError as e:
            raise ValueError(f'"{field.name}" metadata is missing the column parameter information.') from e
        
        return cls(
            attr_name=field.name,
            type_hint=field.type,
            params=params,
        )
    
    def sqlalchemy_column(self) -> sqlalchemy.Column:
        '''Get a sqlalchemy column from this column info.'''
        args = [self.params]

        if self.params.foreign_key is not None:
            args.append(sqlalchemy.ForeignKey(self.params.foreign_key))
        
        column_type = self.dtype(*self.dtype_args, **self.dtype_kwargs)
        return sqlalchemy.Column(name, column_type, **self.column_kwargs)

    def column_type(self) -> sqlalchemy.TypeClause:
        '''Get a sqlalchemy column from this column info.'''
        if self.params.sqlalchemy_type is not None:
            return self.params.sqlalchemy_type
        else:
            return type_hint_to_column_type[self.type_hint](**self.params.type_kwargs)
        
