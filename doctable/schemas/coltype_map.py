
import datetime
import sqlalchemy as sa

from .custom_coltypes import CpickleType, PickleFileType, TextFileType, FileTypeBase, JSONType#, ParseTreeType

#type_lookup = {
python_to_slqlchemy_type = {
    int: sa.Integer,
    float: sa.Float,
    str: sa.String,
    bool: sa.Boolean,
    datetime.datetime: sa.DateTime,
    datetime.time: sa.Time,
    datetime.date: sa.Date,
}

constraint_lookup = {
    'check': sa.CheckConstraint,
    'unique': sa.UniqueConstraint,
    'primarykey': sa.PrimaryKeyConstraint,
    'foreignkey': sa.ForeignKeyConstraint,
}


#column_type_map
string_to_sqlalchemy_type = {
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
    #'pickle':sa.PickleType,
    'smallinteger':sa.SmallInteger,
    'string':sa.String,
    'text':sa.Text,
    'time':sa.Time,
    'unicode':sa.Unicode,
    'unicodetext':sa.UnicodeText,
    'json': JSONType, # custom datatype
    'pickle': CpickleType, # custom datatype
    #'parsetree': ParseTreeType, # custom datatype
    'picklefile': PickleFileType,
    'textfile': TextFileType,
}



