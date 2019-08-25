
# DocTable2 SQLAlchemy Interface

Because DocTable2 was built on SQLAlchemy, this reference provides a guide to some of the DocTable2 --> SQLAlchemy engine functionality mappings.



## Data Types

As a thin interface over the SQLAlchemy core engine, I map each SQLAlchemy data type to a string which is to be used in the DocTable schema definition. You can see the full mapping list below.

For a full description of each of the sqlalchemy data types, see [the SQLAlchemy dat type reference manual](https://docs.sqlalchemy.org/en/13/core/type_basics.html).

type_map = {
    'biginteger':sa.BigInteger,
    'boolean':sa.Boolean,
    'date':sa.Date,
    'datetime':sa.DateTime,
    'enum':sa.Enum,
    'float':sa.Float,
    'integer':sa.Integer,
    'interval':sa.Interval,
    'largebinary':sa.LargeBinary,
    'numeric':sa.Numeric,
    'pickle':sa.PickleType,
    'smallinteger':sa.SmallInteger,
    'string':sa.String,
    'text':sa.Text,
    'time':sa.Time,
    'unicode':sa.Unicode,
    'unicodetext':sa.UnicodeText,
}
custom_types = (
    #'tokens',
    'subdoc',
    'bigblob',
)

