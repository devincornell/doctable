
import sqlalchemy
import typing
import random


class Index:
    name: str
    columns: typing.List[sqlalchemy.Column]
    index_kwargs: typing.Dict[str, typing.Any]
    
    def __init__(self, name: str, *columns, **index_kwargs):
        self.name = name
        self.columns = columns
        self.index_kwargs = index_kwargs
        
        # get rnadom name if needed
        
    def get_sqlalchemy_index(self, 
            col_lookup: typing.Dict[str, sqlalchemy.Column],
        ) -> sqlalchemy.Index:
        '''Convert this index to an sqlalchemy index with references to the table object.
            NOTE: will convert string column names to column objs.
        '''
        cols = [col_lookup[c] if isinstance(c,str) else c for c in self.columns]
        return sqlalchemy.Index(self.name, *cols, **self.index_kwargs)

