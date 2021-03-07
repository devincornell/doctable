
import sqlalchemy as sa
from dataclasses import dataclass, field, fields


class SQLAlchemyConverter()
    type_lookup = {
        int: sa.Integer,
        float: sa.Float,
        str: sa.String,
        bool: sa.Boolean,
        datetime.datetime: sa.DateTime,
        datetime.time: sa.Time,
        datetime.date: sa.Date,
    }
    def __init__(self, row_obj, indices, constraints):
        self.row = row_obj
        self.indices = indices
        self.constraints = constraints
    
    def sqlalchemy_columns(self):
        columns = list()
        
        # regular data columns
        for f in fields(self.row):
            if f.init:
                use_type = self.type_lookup.get(f.type, sa.PickleType)
                col = sa.Column(f.name, use_type, **f.metadata)
                columns.append(col)

        # indices
        if self.indices is not None:
            for name, (cols, kwargs) in self.indices.items():
                columns.append(sa.Index(name, *cols, **kwargs))

        if self.constraints is not None:
            for ctype,  in constraints:

        return column