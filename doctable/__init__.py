name = "doctable"

# expose some features of sqlalchemy
from sqlalchemy.sql import and_, or_, not_

# submodules (future?)
#from .parse import *
#from .doctable import *

# convenience classes and functions
from .migration import migrate_db
from .util import list_tables, read_pickle, write_pickle, showstopper
from .timer import Timer

# regular table features
from .dataclass_schemas import *
from .doctable import DocTable
from .schemas import parse_schema, column_type_map
from .connectengine import ConnectEngine
from .bootstrap import DocBootstrap
#import dataclass_schemas

from .parsing import *

# all legacy
from .docparser import DocParser
from .doctablelegacy import DocTableLegacy

__all__ = ['dataclass_schemas']
