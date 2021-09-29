'''
# What is doctable?

doctable is a python package for designing and manipulating database tables through an object-oriented interface. Read more on the [doctable website](doctable.org).

# Resources

* [doctable website](doctable.org)
* [PyPi page](https://pypi.org/project/doctable/)
* [Github page](https://github.com/devincornell/doctable)

'''




name = "doctable"

# expose some features of sqlalchemy
from sqlalchemy.sql import and_, or_, not_

# main doctable interface
from .doctable import DocTable
from .doctablemongo import DocTableMongo
from .connectengine import ConnectEngine

# legacy interfaces
from .legacy import DocTableLegacy
from .legacy import DocParser


# modules
from .schemas import *
from .parse import *
from .textmodels import *
from .models import *
from .api import *
from .parallel import *
from .util import *
from .dbutils import list_tables, migrate_db

# submodules (future?)
#from .parse import *
#from .doctable import *

# convenience classes and functions



#__all__ = ['parse', 'schemas', 'util', 'model']
