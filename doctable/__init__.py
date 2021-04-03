name = "doctable"

# expose some features of sqlalchemy
from sqlalchemy.sql import and_, or_, not_

# submodules (future?)
#from .parse import *
#from .doctable import *

# convenience classes and functions
from .util import read_pickle, write_pickle, read_json, write_json, showstopper, Timer, FSStore
from .dbutils import list_tables, migrate_db
from .benchmark import *
from .parsing import *

# regular table features
from .dataclass_schemas import *
from .doctable import DocTable
from .schemas import parse_schema, column_type_map
from .connectengine import ConnectEngine
from .bootstrap import DocBootstrap


# all legacy
from .doctablelegacy import DocTableLegacy

__all__ = ['dataclass_schemas', 'parsing', 'util']
