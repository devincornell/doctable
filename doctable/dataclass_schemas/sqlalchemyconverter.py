
import datetime
import sqlalchemy as sa
from dataclasses import dataclass, field, fields


class SQLAlchemyConverter():
    type_lookup = {
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
    def __init__(self, row_obj):
        self.row = row_obj
    
    def get_sqlalchemy_columns(self):
        columns = list()
        
        # regular data columns (uses dataclass features)
        for f in fields(self.row):
            if f.init:
                use_type = self.type_lookup.get(f.type, sa.PickleType)
                col = sa.Column(f.name, use_type, **f.metadata)
                columns.append(col)

        #__indices__ = {
        #    'my_index': ('c1', 'c2', {'unique':True}),
        #    'other_index': ('c1',),
        #}
        if hasattr(self.row, '__indices__') and self.row.__indices__ is not None:
            for name, vals in self.row.__indices__.items():
                args, kwargs = self.get_kwargs(vals)
                columns.append(sa.Index(name, *args, **kwargs))

        #__constraints__ = (
        #    ('check', 'x > 3', dict(name='salary_check')), 
        #    ('foreignkey', ('a','b'), ('c','d'))
        #)
        if hasattr(self.row, '__constraints__') and self.row.__constraints__ is not None:
            for vals in self.row.__constraints__:
                args, kwargs = self.get_kwargs(vals)
                columns.append(self.constraint_lookup[args[0]](*args[1:], **kwargs))

        return columns

    @staticmethod
    def get_kwargs(vals):
        args = vals[:-1] if isinstance(vals[-1], dict) else vals
        kwargs = vals[-1] if isinstance(vals[-1], dict) else dict()
        print(f'args={args}, kwargs={kwargs}')
        return args, kwargs
