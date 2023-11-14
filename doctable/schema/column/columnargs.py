from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

from ..missing import MISSING





COLUMN_METADATA_ATTRIBUTE_NAME = '_column_args'

def has_column_args(field: dataclasses.Field) -> bool:
    '''Check if a dataclass field has column args.'''
    return COLUMN_METADATA_ATTRIBUTE_NAME in field.metadata

def get_column_args(field: dataclasses.Field) -> ColumnArgs:
    '''Get the column args from a dataclass field.'''
    try:
        return field.metadata[COLUMN_METADATA_ATTRIBUTE_NAME]
    except KeyError as e:
        raise KeyError(f'"{field.name}" does not have column args attached. '
            'Use table_schema decorator to add column args.') from e

def set_column_args(metadata: typing.Dict[str,typing.Any], column_args: ColumnArgs):
    '''Check if a dataclass field has column args.'''
    #setattr(metadata, COLUMN_METADATA_ATTRIBUTE_NAME, column_args)
    metadata[COLUMN_METADATA_ATTRIBUTE_NAME] = column_args



@dataclasses.dataclass
class ColumnArgs:
    '''Args to be passed to sqlalchemy.Column. Used by client directly through constructor.
        Read more about sqlalchemy.Column here:
        https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Column.__init__
    Args:
        order: order of column in table (non-numbered appear after numbered)
        column_name: use when column is different from object attribute
        type_kwargs: keyword arguments to pass to sqlalchemy type. only used when type inferred from python type hint
        use_type: use this type instead of inferring from python type hint
        sqlalchemy_type: type of column in database using sqlachemy types (any kwargs should be passed directly here)
        autoincrement: whether to autoincrement the column
        nullable: whether the column can be null
        unique: whether the column is unique
        primary_key: whether the column is a primary key
        index: whether the column is indexed
        foreign_key: name of the column (tabname.colname) that this column references
        default: default value for column
        onupdate: function to call when column is updated
        server_default: default value for column on server side
        server_onupdate: function to call when column is updated on server side
        comment: comment to add to column in database
        other_kwargs: see Column.__init__ link above for any other kwargs not listed here
    '''
    order: int = float('inf')
    column_name: str = None
    type_kwargs: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    use_type: typing.Optional[typing.Type] = None
    sqlalchemy_type: typing.Optional[sqlalchemy.TypeClause] = None# provide an sqlalchemy type
    autoincrement: bool = False
    nullable: bool = True
    unique: bool = None
    primary_key: bool = False
    index: bool = None
    foreign_key: str = None
    default: str = None 
    onupdate: typing.Callable[[],typing.Any] = None
    server_default: typing.Union[str, sqlalchemy.FetchedValue, sqlalchemy.Text] = None
    server_onupdate: sqlalchemy.FetchedValue = None
    comment: str = None
    other_kwargs: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        self.check_valid()

    def check_valid(self):
        '''Used to check whether the result is valid after creation.'''
        if self.sqlalchemy_type is not None and len(self.type_kwargs) > 0:
            raise ValueError('Only one of sqlalchemy_type and type_kwargs can '
                f'be provided. Add the kwargs to the type directly instead.')    
        if self.use_type is not None and self.sqlalchemy_type is not None:
            raise ValueError('Only one of use_type and sqlalchemy_type can '
                f'be provided. Use sqlalchemy_type to pass kwargs to type.')
    
    def sqlalchemy_foreign_key(self) -> typing.Union[sqlalchemy.ForeignKey, None]:
        '''Get a foreign key object or None.'''
        return sqlalchemy.ForeignKey(self.foreign_key) if self.foreign_key is not None else None
    
    def sqlalchemy_column_kwargs(self) -> typing.Dict[str, typing.Any]:
        return dict(
            autoincrement=self.autoincrement,
            nullable=self.nullable,
            unique=self.unique,
            primary_key=self.primary_key,
            index=self.index,
            default=self.default,
            onupdate=self.onupdate,
            server_default=self.server_default,
            server_onupdate=self.server_onupdate,
            comment=self.comment,
            **self.other_kwargs,
        )
