name = "doctable"

# expose some features of sqlalchemy
from sqlalchemy.sql import and_, or_, not_

from .doctable import DocTable
from .doctable2 import DocTable2

from .migration import migrate_db

