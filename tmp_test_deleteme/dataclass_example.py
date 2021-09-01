#!/usr/bin/env python
# coding: utf-8

# # Dataclass Schema Example
# In this vignette I'll show how to use a [Python dataclass](https://realpython.com/python-data-classes/) (introduced in Python 3.7) to specify a schema for a DocTable. The advantage of this schema format is that you can use custom classes to represent each row, and easily convert your existing python objects into a format that it easy to store in a sqlite database.

# In[1]:


from datetime import datetime
from pprint import pprint
import pandas as pd

import sys
sys.path.append('..')
import doctable


# ## Basic dataclass usage
# For our first example, we show how a basic dataclass object can be used as a DocTable schema. First we create a python dataclass using the `@dataclass` decorator. This object has three members, each defaulted to `None`. We can create this object using the constructor provided by `dataclass`.

# In[2]:


from dataclasses import dataclass
@doctable.schema
class User:
    __slots__ = []
    name: str = None
    age: int = None
    height: float = None
User()


# And it is relatively easy to create a new doctable using the schema provided by our dataclass `User` by providing the class definition to the `schema` argument. We can see that `DocTable` uses the dataclass schema to create a new table that follows the specified Python datatypes.

# In[3]:


db = doctable.DocTable(schema=User, target=':memory:')
db.schema_table()


# Now we insert several new objects into the table and view them using `DocTable.head()`. Note that the datbase actually inserted the object's defaulted values into the table.

# In[4]:


db.insert([User('kevin'), User('tyrone', age=12), User('carlos', age=25, height=6.5)])
db.head()


# Using a normal `select()`, we can extract the results as the original objects. With no parameters, the select statement extracts all columns as they are stored and they exactly match the original data we entered. As expected from the python object, we can access these as properties of the object. Due to the base class `doctable.DocTableRow`, we can also access properties using the `__getitem__` indexing. I'll show why there is a difference btween the two later.

# In[5]:


users = db.select()
for user in users:
    print(f"{user.name}:\n\tage: {user.age}\n\theight: {user['height']}")


# ## Example using `doctable.Col`
# In this example, we will show how to create a dataclass with functionality that supports more complicated database operations. A key to this approach is to use the `doctable.Col` function as default values for our parameters. Note that when we initialize the object, the default values of all columns except for `name` are set to `EmptyValue`. This is important, because `EmptyValue` will indicate values that are not meant to be inserted into the database or are not retrieved from the database after selecting.

# In[6]:


@doctable.schema
class User:
    __slots__ = []
    name: str = doctable.Col()
    age: int = doctable.Col()
    height: float = doctable.Col()
User()


# Given that the type specifications are the same as the previous example, we get exactly the same database schema. We insert entries just as before. The `User` data contained `EmptyValue`s, and so that column data was not presented to the database at all - instead, the schema's column defaults were used. Consistent with our schema (not the object defaults, the default values were set to None.

# In[7]:


db = doctable.DocTable(schema=User, target=':memory:')
print(db.schema_table())
db.insert([User('kevin'), User('tyrone', age=12), User('carlos', age=25, height=6.5)])
for user in db.select():
    print(f"{user}")


# Now let's try to select only a subset of the columns - in this case, 'name' and 'age'.

# In[8]:


users = db.select(['name', 'age'])
users[0]


# Note that the user height was set to `EmptyValue`. When we try to access height as an index, we get an error indicating that the data was not retrived in the select statement.

# In[9]:


try:
    users[0]['height']
except KeyError as e:
    print(e)


# On the contrary, if we try to access as an attribute, the actual `EmptyValue` object is retrieved. Object properties work as they always have, but indexing into columns will check for errors in the program logic. This implementation shows how dataclass schemas walk the line between regular python objects and database rows, and thus accessing these values can be done differently depending on how much the table entries should be treated like regular objects vs database rows. This is all determined based on how the dataclass columns are configured.

# In[10]:


users[0].height


# ## Special column types
# Now I'll introduce two special data column types provided by doctable: `IDCol()`, which represents a regular id column in sqlite with autoindex and primary_key parameters set, and `UpdatedCol()`, which records the datetime that an object was added to the database. When we create a new user using the dataclass constructor, these values are set to `EmptyValue`, and are relevant primarily to the database. By setting the `repr` parameter in the `@dataclass` decorator, we can use the `__repr__` of the `DocTableRow` base class, which hides `EmptyValue` columns. This is optional.

# In[11]:


from dataclasses import field, fields
@doctable.schema(repr=False)
class User:
    __slots__ = []
    id: int = doctable.IDCol() # shortcut for autoindex, primary_key column.
    updated: datetime = doctable.UpdatedCol() # shortcut for automatically 
    
    name: str = doctable.Col(nullable=False)
    age: int = doctable.Col(None) # accessing sqlalchemy column keywords arguments

user = User(name='carlos', age=15)
user


# And we can see the relevance of those columns by inserting them into the database and selecting them again. You can see from the result of `.head()` that the primary key `id` and the `updated` columns were appropriately filled upon insertion. After selecting, these objects also contain valid values.

# In[12]:


db = doctable.DocTable(schema=User, target=':memory:')
print(db.schema_table())
db.insert([User(name='kevin'), User(name='tyrone', age=12), User(name='carlos', age=25)])
db.head()


# This was just an example of how regular Python dataclass objects can contain additional data which is relevant to the database, but which is otherwise unneeded. After retrieving from database, we can also use `.update()` to modify the entry.

# In[13]:


user = db.select_first()
user.age = 10
db.update(user, where=db['id']==user['id'])
db.head()


# We can use the convenience function `update_dataclass()` to update a single row corresponding to the object.

# In[14]:


user.age = 11
db.update_dataclass(user)
db.head()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




