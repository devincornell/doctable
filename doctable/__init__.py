from .connectcore import ConnectCore, TableAlreadyExistsError, TableDoesNotExistError
from .query import *
from .schema import *
from .dbtable import *

name = "doctable"

# expose some features of sqlalchemy
import sqlalchemy

class f:
    max = sqlalchemy.sql.func.max
    min = sqlalchemy.sql.func.min
    count = sqlalchemy.sql.func.count
    sum = sqlalchemy.sql.func.sum

    distinct = sqlalchemy.sql.expression.distinct
    between = sqlalchemy.sql.expression.between
    
    all_ = sqlalchemy.sql.expression.all_
    and_ = sqlalchemy.sql.expression.and_
    or_ = sqlalchemy.sql.expression.or_
    not_ = sqlalchemy.sql.expression.not_

    desc = sqlalchemy.sql.expression.desc
    asc = sqlalchemy.sql.expression.asc
    
    any_ = sqlalchemy.sql.expression.any_
    alias = sqlalchemy.sql.expression.alias
    between = sqlalchemy.sql.expression.between


