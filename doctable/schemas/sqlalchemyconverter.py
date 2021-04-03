
import datetime
import sqlalchemy as sa
from dataclasses import dataclass, field, fields
from .coltype_map import python_to_slqlchemy_type, string_to_sqlalchemy_type, constraint_lookup

class SQLAlchemyConverter():

    def __init__(self, row_obj):
        self.row = row_obj
    
    def get_sqlalchemy_columns(self):
        columns = list()
        
        # regular data columns (uses dataclass features)
        for f in fields(self.row):
            if f.init:
                use_type = python_to_slqlchemy_type.get(f.type, sa.PickleType)
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
                columns.append(constraint_lookup[args[0]](*args[1:], **kwargs))

        return columns

    @staticmethod
    def get_kwargs(vals):
        args = vals[:-1] if isinstance(vals[-1], dict) else vals
        kwargs = vals[-1] if isinstance(vals[-1], dict) else dict()
        #print(f'args={args}, kwargs={kwargs}')
        return args, kwargs
