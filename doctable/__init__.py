'''

# What is doctable?

doctable is a python package for designing and manipulating database tables through an object-oriented interface without the overhead of ORM. Read more on [doctable.org](https://doctable.org).

# Important Objects

* [DocTable](doctable/doctable.html)
* [ConnectEngine](doctable/connectengine.html)

* [ParsePipeline](doctable/parse/pipeline.html)
* [Parsing Functions](doctable/parse/parsefuncs.html)
* [ParseTree](doctable/parse/parsetree.html)

* [Stepper](doctable/util/stepper.html)
* [FSStore](doctable/util/fsstore.html)
* [TempFolder](doctable/util/tempfolder.html)
* [I/O Functions](doctable/util/io.html)





# Additional Resources

[PyPi page](https://pypi.org/project/doctable/)

[Github page](https://github.com/devincornell/doctable)

'''




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




# main doctable interface
from .doctable import DocTable
from .doctablemongo import DocTableMongo
from .connectengine import ConnectEngine

# legacy interfaces
from .legacy import DocTableLegacy
from .legacy import DocParser


# modules
from .schemas import *
from .schema import *
from .parse import *
from .textmodels import *
from .models import *
from .api import *
#from .parallel import *
from .util import *
from .stepper import *
from .dbutils import list_tables, migrate_db

# submodules (future?)
#from .parse import *
#from .doctable import *

# convenience classes and functions



#__all__ = ['parse', 'schemas', 'util', 'model']
