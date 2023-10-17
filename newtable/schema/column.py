from __future__ import annotations

import typing
import dataclasses
import sqlalchemy
import datetime

from .missing import MISSING

COLUMN_METADATA_ATTRIBUTE_NAME = '_column_args'

def get_column_args(field: dataclasses.Field) -> ColumnArgs:
    '''Get the column args from a dataclass field.'''
    try:
        return field.metadata[COLUMN_METADATA_ATTRIBUTE_NAME]
    except KeyError as e:
        raise KeyError(f'"{field.name}" does not have column args attached. '
            'Use table_schema decorator to add column args.') from e

def has_column_args(field: dataclasses.Field) -> bool:
    '''Check if a dataclass field has column args.'''
    return COLUMN_METADATA_ATTRIBUTE_NAME in field.metadata

type_hint_to_column_type = {
    int: sqlalchemy.Integer,
    str: sqlalchemy.String,
    float: sqlalchemy.Float,
    bool: sqlalchemy.Boolean,
    datetime.datetime: sqlalchemy.DateTime, # NOTE: datetime.datetime is subclass of datetime.date
    datetime.time: sqlalchemy.Time,
    datetime.date: sqlalchemy.Date,
    bytes: sqlalchemy.LargeBinary,
    typing.Any: sqlalchemy.PickleType,
}


def Column(
    field_args: FieldArgs = None,
    column_args: ColumnArgs = None,
) -> dataclasses.field:
    '''Record column information in the metadata of a dataclass field.'''
    field_args = field_args if field_args is not None else FieldArgs()
    column_args = column_args if column_args is not None else ColumnArgs()

    return dataclasses.field(
        metadata={
            **field_args.metadata, 
            COLUMN_METADATA_ATTRIBUTE_NAME: column_args,
        },
        **field_args.dict_without_metadata()
    )

@dataclasses.dataclass
class FieldArgs:
    '''Creates kwargs dict to be passed to dataclasses.field. Read about args here:
        https://docs.python.org/3/library/dataclasses.html
    '''
    default: typing.Any = MISSING # dataclass.field: default value for column
    default_factory: typing.Optional[typing.Callable[[], typing.Any]] = MISSING # default factory for column
    repr: bool = True # dataclass.field: whether to include in repr
    hash: bool = None # dataclass.field: whether to include in hash
    init: bool = True # dataclass.field: whether to include in init
    compare: bool = True # dataclass.field: whether to include in comparison
    kw_only: bool = MISSING # dataclass.field: whether to include in kw_only
    metadata: typing.Optional[typing.Dict[str, typing.Any]] = None # dataclass.field: metadata to include in field

    def dict_without_metadata(self) -> typing.Dict[str, typing.Any]:
        v = dataclasses.asdict(self)
        del v['metadata']
        return v

@dataclasses.dataclass
class ColumnArgs:
    '''Args to be passed to sqlalchemy.Column. Used by client directly through constructor.
        Read more about sqlalchemy.Column here:
        https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Column.__init__
    Args:
        order: order of column in table (non-numbered appear after numbered)
        column_name: use when column is different from object attribute
        type_kwargs: keyword arguments to pass to sqlalchemy type. only used when type inferred from python type hint
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

    def sqlalchemy_column(self, 
        type_hint: typing.Union[str, type], 
        attr_name: str
    ) -> sqlalchemy.Column:
        '''Get a sqlalchemy column from this column info.
            Raises KeyError if there is no match.
        '''
        if self.column_name is not None:
            name = self.column_name
        else:
            name = attr_name

        return sqlalchemy.Column(
            name=name,
            *self.column_type_args(type_hint),
            **self.sqlalchemy_column_kwargs(),
        )

    def column_type_args(self, type_hint: typing.Union[type, str]) -> typing.Tuple[sqlalchemy.TypeClause]:
        if sum([self.sqlalchemy_type is not None, self.type_kwargs]) > 1:
            raise ValueError('Only one of sqlalchemy_type and type_hint can be provided.')
        
        fk = (sqlalchemy.ForeignKey(self.foreign_key),) if self.foreign_key is not None else ()

        if self.sqlalchemy_type is not None:
            return self.sqlalchemy_type + fk
        elif self.foreign_key is not None:
            return fk
        else:
            for mth, mct in type_hint_to_column_type.items():
                if issubclass(type_hint, mth): # type hints are types
                    return mct(**self.type_kwargs)
                elif type_hint == mth: # type hints are strings
                    return mct(**self.type_kwargs)
            raise TypeError(f'"{type_hint}" does not map to a valid column '
                f'type. Choose one of {type_hint_to_column_type.keys()}')

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

@dataclasses.dataclass
class ColumnInfo:
    '''Contains all information needed to create a column in a database.'''
    attr_name: str # name of attribute in data container
    type_hint: type
    column_args: ColumnArgs
    
    @classmethod
    def default(cls, attr_name: str, type_hint: type) -> ColumnInfo:
        '''Get column info from only a sqlalchemy type.'''
        return cls(
            attr_name=attr_name,
            type_hint=type_hint,
            column_args=ColumnArgs(),
        )

    @classmethod
    def from_field(cls, field: dataclasses.Field) -> ColumnInfo:
        '''Get column info from a dataclass field after dataclass is created.'''
        return cls(
            attr_name=field.name,
            type_hint=field.type,
            column_args=get_column_args(field) if has_column_args(field) else ColumnArgs(),
        )
    
    def sqlalchemy_column(self) -> sqlalchemy.Column:
        '''Get a sqlalchemy column from this column info.'''
        return self.column_args.sqlalchemy_column(
            type_hint=self.type_hint,
            attr_name=self.attr_name,
        )

    def compare_key(self) -> typing.Tuple[float, str]:
        return (self.column_args.order, self.final_name())
    
    def name_translation(self) -> typing.Tuple[str, typing.Optional[str]]:
        '''Get (attribute, column) name pairs.'''
        return self.attr_name, self.final_name()
    
    def final_name(self) -> str:
        if self.column_args.column_name is None:
            return self.attr_name
        else:
            return self.column_args.column_name



