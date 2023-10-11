from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

COLUMN_METADATA_ATTRIBUTE_NAME = '_column_args'

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

def id_column(
    column_name: typing.Optional[str] = None, # name of the column in the database
    type_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, # keyword arguments to pass to sqlalchemy type. ignored if sqlalchemy_type is specified
    dataclass_field: typing.Optional[typing.Dict[str, typing.Any]] = None, # keyword arguments to pass to dataclass.field
    **column_kwargs # pass to sqlalchemy.Column. ex: primary_key=True, nullable=True, etc.
) -> dataclasses.field:
    return column(
        column_name=column_name,
        sqlalchemy_type=sqlalchemy.Integer,
        type_kwargs=type_kwargs,
        dataclass_field=dataclass_field,
        primary_key=True,
        autoincrement=True,
        **column_kwargs,
    )

def column(
    column_name: typing.Optional[str] = None, # name of the column in the database
    sqlalchemy_type: typing.Optional[sqlalchemy.TypeClause] = None, # type of column in database using sqlachemy types
    foreign_key: str = None, # name of the column (tabname.colname) that this column references
    type_kwargs: typing.Optional[typing.Dict[str, typing.Any]] = None, # keyword arguments to pass to sqlalchemy type. ignored if sqlalchemy_type is specified
    dataclass_field: typing.Optional[typing.Dict[str, typing.Any]] = None, # keyword arguments to pass to dataclass.field
    **column_kwargs # pass to sqlalchemy.Column. ex: primary_key=True, nullable=True, etc.
) -> dataclasses.field:
    '''Record column information in the metadata of a dataclass field.'''
    return dataclasses.field(
        metadata={
            **dataclass_field.get('metadata', {}), 
            COLUMN_METADATA_ATTRIBUTE_NAME: ColumnParams(
                column_name=column_name,
                sqlalchemy_type=sqlalchemy_type,
                foreign_key=foreign_key,
                type_kwargs=type_kwargs,
                column_kwargs=column_kwargs,
                dataclass_field=dataclass_field,
            ),
        },
        **dataclass_field
    )


@dataclasses.dataclass
class ColumnParams:
    '''Contains user-specified parameters for a column.'''
    column_name: typing.Optional[str]
    sqlalchemy_type: typing.Optional[sqlalchemy.TypeClause]
    foreign_key: typing.Optional[str]
    type_kwargs: typing.Dict[str, typing.Any]
    column_kwargs: typing.Dict[str, typing.Any]
    dataclass_field: typing.Optional[typing.Dict[str, typing.Any]]

    @classmethod
    def default(cls) -> ColumnParams:
        return cls(
            column_name=None,
            sqlalchemy_type=None,
            foreign_key=None,
            type_kwargs={},
            column_kwargs={},
            dataclass_field=None,
        )

    def sqlalchemy_column(self, 
        type_hint: typing.Union[str, type], 
        attr_name: str
    ) -> sqlalchemy.Column:
        '''Get a sqlalchemy column from this column info.
            Raises KeyError if there is no match.
        '''
        if self.column_name is not None:
            if self.column_name != attr_name:
                raise ValueError(f'Specified column name "{self.column_name}" does not match attribute name "{attr_name}".')
            name = self.column_name
        else:
            name = attr_name

        fk = (sqlalchemy.ForeignKey(self.foreign_key),) if self.foreign_key is not None else ()
        
        if self.sqlalchemy_type is not None:
            args = (self.sqlalchemy_type,) + fk
        elif self.foreign_key is not None:
            args = fk
        else:
            try:
                args = (type_hint_to_column_type[type_hint](**self.type_kwargs),) + fk
            except KeyError as e:
                raise KeyError(f'"{attr_name}" type hint "{type_hint}" was not found '
                    f'in the list of valid mappings: {type_hint_to_column_type}.') from e

        return sqlalchemy.Column(
            name=name,
            *args,
            **self.column_kwargs,
        )


@dataclasses.dataclass
class ColumnInfo:
    '''Contains all information needed to create a column in a database.'''
    attr_name: str # name of attribute in data container
    type_hint: type
    params: ColumnParams
    
    @classmethod
    def default(cls, attr_name: str, type_hint: type) -> ColumnInfo:
        '''Get column info from only a sqlalchemy type.'''
        return cls(
            attr_name=attr_name,
            type_hint=type_hint,
            params=ColumnParams.default(),
        )

    @classmethod
    def from_field(cls, field: dataclasses.Field) -> ColumnInfo:
        '''Get column info from a dataclass field.'''
        if COLUMN_METADATA_ATTRIBUTE_NAME in field.metadata:
            params = field.metadata[COLUMN_METADATA_ATTRIBUTE_NAME]
        else:
            params = ColumnParams.default()
        
        return cls(
            attr_name=field.name,
            type_hint=field.type,
            params=params,
        )
    
    def name_pair(self) -> typing.Tuple[str, typing.Optional[str]]:
        '''Get the attribute name and column name.'''
        return self.attr_name, self.params.column_name
    
    def sqlalchemy_column(self) -> sqlalchemy.Column:
        '''Get a sqlalchemy column from this column info.'''
        return self.params.sqlalchemy_column(
            type_hint=self.type_hint,
            attr_name=self.attr_name,
        )

