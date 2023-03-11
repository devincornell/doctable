
import typing
import datetime
import sqlalchemy as sa

from doctable.textmodels import ParseTreeDoc
from .custom_coltypes import CpickleType, ParseTreeDocFileType, PickleFileType, TextFileType, FileTypeBase, JSONType#, ParseTreeType


python_to_slqlchemy_type = {
    int: sa.Integer,
    float: sa.Float,
    str: sa.String,
    bool: sa.Boolean,
    datetime.datetime: sa.DateTime,
    datetime.time: sa.Time,
    datetime.date: sa.Date,
    ParseTreeDoc: ParseTreeDocFileType,
    bytes: sa.LargeBinary,
    JSONType: JSONType,
    typing.Any: sa.PickleType,
}
# this works for newer versions of python where type hints are strings
for pytype, satype in list(python_to_slqlchemy_type.items()):
    python_to_slqlchemy_type[str(pytype)] = satype

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
    'parsetree': ParseTreeDocFileType, # custom datatype
    'picklefile': PickleFileType,
    'textfile': TextFileType,
}



