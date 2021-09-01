#!/usr/bin/env python
# coding: utf-8

# # DocTable Schemas
# There are two ways to define schemas for a DocTable:
# 
# 1. **dataclass schema**: column names and types come from a class created using the `@doctable.schema` decorator. This class represents a single row, and is returned by default when a select query is executed. `doctable` provides a thin layer over [dataclasses](https://realpython.com/python-data-classes/) with slots to reduce memory overhead from returned results. Custom methods can also be defined on the class that will not affect the database schema. When using this method, constraints and indices must be provided at the time of `DocTable` instantiation (or in the definition of an inheriting `DocTable`).
# 
# 2. **list schema**: column names and types come from sequences of strings according to a custom doctable format. This method requires less knowledge of doctable objects but otherwise has no advantages over dataclass schemas.
# 
# The doctable package builds on sqlalchemy, so both types of schema specifications ultimately result in a sequence of [`sqlalchemy` column types](https://docs.sqlalchemy.org/en/13/core/type_basics.html) that will be used to construct (or interface with) the database table.

# In[1]:


from datetime import datetime
from pprint import pprint
import pandas as pd

import sys
sys.path.append('..')
import doctable


# ## Schema Type Mappings
# There are two lookup tables used to relate to sqlalchemy column types. The first is a map from Python datatypes to the sqlalchemy types. This is sufficient for the simplest possible dataclass schema specification.

# In[2]:


doctable.python_to_slqlchemy_type


# The second is a string lookup that is provided for the list schema format. You can see that this offers a larger number of types compared to the Python type conversion.

# ## Dataclass Schemas Using `doctable.schema` Decorator
# 
# A dataclass schema is created by defining a class using the `@doctable.schema` decorator. This object will represent a single row in the table, and column names/schemas will be inferred from the variable names and type hints, respectively. The simplest possible version looks like a regular dataclass, except that `__slots__` should be defined so that the decorator can automatically add the columns as slots (this can be overridden using `require_slots=False` in the decorator).

# In[18]:


@doctable.schema
class Record:
    __slots__ = []
    name: str = None
    age: int = None

# the schema that would result from this dataclass:
doctable.DocTable(target=':memory:', schema=Record).schema_table()


# It looks like a regular dataclass - and, in fact, it is a dataclass! The decorator essentially converts your class into a dataclass that inherits from `doctable.DocTableRow`, so it has a few extra methods. I'll show later why this matters, but it is slightly preferable to access member variables through subscripting (defined via `__getitem__`). The  base class also defines a `__repr__` and a `.as_dict()` method to convert to a dictionary.

# In[20]:


r = Record('Devin Cornell', 30)
r, r['name'], r['age'], r.as_dict()


# To add functionality beyond dataclasses, doctable provides a `Col` function that can be used as the default value in the class definition. This allows you to access both doctable schema features and pass parameters to the `dataclasses.field` function. Using `Col` also sets the default value to a special class called `doctable.EmptyValue`, which, among other things, will not show up in the class `__repr__`. Notice that I use `Col` to create the `id` column we have come to expect in most sql tables.

# In[12]:


@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.Col(primary_key=True, autoincrement=True) # can also use doctable.IDCol() as a shortcut
    name: str = doctable.Col()
    age: int = doctable.Col()

# the schema that would result from this dataclass:
doctable.DocTable(target=':memory:', schema=Record).schema_table()


# There are several other custom column types I included for convenience.

# In[21]:


import datetime
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol() # auto-increment primary key
    added: datetime = doctable. AddedCol() # record when row was added
    updated: datetime = doctable.UpdatedCol() # record when row was updated
    name: str = doctable.Col()
    is_old: bool = doctable.Col()

# the schema that would result from this dataclass:
doctable.DocTable(target=':memory:', schema=Record).schema_table()


# In[ ]:





# In[ ]:





# In[3]:


doctable.string_to_sqlalchemy_type


# In[4]:


from datetime import datetime

@doctable.schema
class Record:
    
    # custom doctable column types
    id: int = doctable.IDCol() # auto-increment primary key
    added: datetime = doctable. AddedCol() # record when row was added
    updated: datetime = doctable.UpdatedCol() # record when row was updated
    
    # generic column object.
    # Keyword arguments are passed directly to sqlalchemy Column constructor
    name: str = doctable.Col(nullable=False)
    
    # first argument is default value or factory (automatically determined)
    num_siblings: int = doctable.Col(0)
        
    # this will be stored as a binary type in sql
    friends: list = doctable.Col(list)
    
    # can also use regular scalar default values
    age: int = 6
    is_old: bool = None
        
    # indices and constraints - these are used by DocTableRow objects
    _indices_ = {
        # SQLAlchemy: Index('name_index', 'name')
        'name_index': ('name',),
        
        # SQLAlchemy: Index('name_age_index', 'name', 'age', unique=True)
        'name_age_index': ('name', 'age', {'unique':True}),
    }
    
    # add constraints to table
    _constraints_ = (
        
        #SQLAlchemy:  UniqueConstraint('name', 'age')
        ('unique', 'name', 'age'),
        
        #SQLAlchemy: CheckConstraint('age > 0', name='check_age')
        ('check', 'age > 0', {'name':'check_age'}), 
        
        #('foreignkey', ('a','b'), ('c','d')),
    )
        
        
    # doctable method to execute after constructor is created
    def __post_init__(self):
        self.is_old = age > 28
        
    # any custom method the user would like to add
    @property
    def num_friends(self):
        return len(self.friends)
    
    
db = doctable.DocTable(target=':memory:', schema=Record)
db.schema_table()


# ## List Schemas
# And this is another example showing the list schema format.

# In[5]:


schema = (
    # standard id column
    #SQLAlchemy: Column('id', Integer, primary_key = True, autoincrement=True), 
    ('integer', 'id', dict(primary_key=True, autoincrement=True)),
    # short form (can't provide any additional args though): ('idcol', 'id')

    # make a category column with two options: "FICTION" and "NONFICTION"
    #SQLAlchemy: Column('title', String,)
    ('string', 'category', dict(nullable=False)),

    # make a non-null title column
    #SQLAlchemy: Column('title', String,)
    ('string', 'title', dict(nullable=False)),

    # make an abstract where the default is an empty string instead of null
    #SQLAlchemy: Column('abstract', String, default='')
    ('string', 'abstract',dict(default='')),

    # make an age column where age must be greater than zero
    #SQLAlchemy: Column('abstract', Integer)
    ('integer', 'age'),

    # make a column that keeps track of column updates
    #SQLAlchemy: Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
    ('datetime', 'updated_on',  dict(default=datetime.now, onupdate=datetime.now)),
    # short form to auto-record update date: ('date_updated', 'updated_on')
    
    #SQLAlchemy: Column('updated_on', DateTime(), default=datetime.now)
    ('datetime', 'updated_on',  dict(default=datetime.now)),
    # short form to auto-record insertion date: ('date_added', 'added_on')

    # make a string column with max of 500 characters
    #SQLAlchemy: Column('abstract', String, default='')
    ('string', 'text',dict(),dict(length=500)),

    
    ##### Custom DocTable Column Types #####
    
    # uses json.dump to convert python object to json when storing and
    # json.load to convert json back to python when querying
    ('json','json_data'),
    
    # stores pickled python object directly in table as BLOB
    # TokensType and ParagraphsType are defined in doctable/coltypes.py
    # SQLAlchemy: Column('tokenized', TokensType), Column('sentencized', ParagraphsType)
    ('pickle','tokenized'),
    
    # store pickled data into a separate file, recording only filename directly in table
    # the 'fpath' argument can specify where the files should be placed, but by
    # default they are stored in <dbname>_<tablename>_<columnname>
    #('picklefile', 'pickle_obj', dict(), dict(fpath='folder_for_picklefiles')),
    
    # very similar to above, but use only when storing text data
    #('textfile', 'text_file'), # similar to above
    
    
    ##### Constraints #####
    
    #SQLAlchemy: CheckConstraint('category in ("FICTION","NONFICTION")', name='salary_check')
    ('check_constraint', 'category in ("FICTION","NONFICTION")', dict(name='salary_check')),
    
    #SQLAlchemy: CheckConstraint('age > 0')
    ('check_constraint', 'age > 0'),
    
    # make sure each category/title entry is unique
    #SQLAlchemy:  UniqueConstraint('category', 'title', name='work_key')
    ('unique_constraint', ['category','title'], dict(name='work_key')),
    
    # makes a foreign key from the 'subkey' column of this table to the 'id'
    # column of ANOTHERDOCTABLE, setting the SQL onupdate and ondelete foreign key constraints
    #('foreignkey_constraint', [['subkey'], [ANOTHERDOCTABLE['id']]], {}, dict(onupdate="CASCADE", ondelete="CASCADE")),
    #NOTE: Can't show here because we didn't make ANOTHERDOCTABLE
    
    ##### Indexes ######
    
    # make index table
    # SQLAlchemy: Index('ind0', 'category', 'title', unique=True)
    ('index', 'ind0', ('category','title'),dict(unique=True)),
    
)
md = doctable.DocTable(target=':memory:', schema=schema, verbose=True)
md.schema_table()

