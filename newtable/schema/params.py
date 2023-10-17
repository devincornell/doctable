
import typing
import dataclasses
import sqlalchemy

@dataclasses.dataclass
class ColumnArgs:
    '''Creates kwargs dict to be passed to sqlalchemy.Column. Read about args here:
        https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.Column.__init__
    Other args:
        column_name: use when column is different from object attribute
        type_kwargs: keyword arguments to pass to sqlalchemy type. only used when type inferred from python type hint
        sqlalchemy_type: type of column in database using sqlachemy types (any kwargs should be passed directly here)
        sql_type: manually type the sql type as a string
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
    column_name: str
    type_kwargs: typing.Dict[str, typing.Any] = dataclasses.field(default_factory=dict)
    sqlalchemy_type: typing.Optional[sqlalchemy.TypeClause] = None# provide an sqlalchemy type
    sql_type: str = None # manually type the sql type
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
    
