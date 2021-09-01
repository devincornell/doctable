#!/usr/bin/env python
# coding: utf-8

# # `DocTable` Overview
# 
# A `DocTable` acts as an object-oriented interface to a single database table. It will maintain a connection to the database and [sqlalchemy](https://docs.sqlalchemy.org/en/14/core/) metadata about the table schema. Schemas are provided as classes that act much like [`dataclasses`](https://realpython.com/python-data-classes/) (see [the doctable schema guide](examples/doctable_schema.html) for more explanation), and indices and constraints are often specified in a definition of a subclass of `DocTable`.
# 
# You may also want to see the [vignettes](examples/example_nss_1_intro.html) for more examples, the [`DocTable` docs](ref/doctable.DocTable.html) for more information about the class, or the [schema guide](examples/doctable_schema.html) for more information about creating schemas. I also recommend looking examples for [insert, delete](examples/doctable_insert_delete.html), [select](examples/doctable_select.html), and [update](examples/doctable_update.html) methods.
# 
# Here I'll just provide some examples to give a sense of how `DocTable` works.

# In[1]:


import random
random.seed(0)
import pandas as pd
import numpy as np
from dataclasses import dataclass

import sys
sys.path.append('..')
import doctable


# # Defining a Database Schema
# 
# `DocTable` schemas are created using the `doctable.schema` decorator on a class that uses `doctable.Col` for defaulted parameters. Check out the [schema guide](examples/doctable_schema.html) for more detail about schema classes. Our demonstration class will include three columns: `id`, `name`, and `age`, with an additional `.is_old` property derived from `age` for example.

# In[2]:


@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col(nullable=False)
    age: int = doctable.Col()

    @property
    def is_old(self):
        return self.age >= 30 # lol


# We can instantiate a `DocTable` by passing a `target` and `schema` (`Record` in our example) parameters, and I show the resulting schema using `.schema_table()`. Note that the type hints were used to describe column types, and `id` was used as the auto-incremented primary key.

# In[3]:


table = doctable.DocTable(target=':memory:', schema=Record)
table.schema_table()


# Probably a more common use case will be to subclass `DocTable` to provide some basic definitions.

# In[4]:


class RecordTable(doctable.DocTable):
    _tabname_ = 'records'
    _schema_ = Record
    _indices_ = (
        doctable.Index('ind_age', 'age'),
    )
    _constraints_ = (
        doctable.Constraint('check', 'age > 0'),
    )

table = RecordTable(target=':memory:')
table


# # Object Interface
# The main goal of doctable was to create an object-oriented interface to working with database tables. To that end, I'll show some of the more common use cases in the following examples.
# 
# First, note that subscripting the table object allows you to access sqlalchemy `Column` objects, which, as I will show a bit later, can be used to create where conditionals for select and update queries.

# In[5]:


table['id']


# As we'll show later, these column objects also have some operators defined such that they can be used to construct complex queries and functions.

# In[6]:


table['id'] > 3


# ## Inserting Rows
# We use the `.insert()` method to insert a row passed as a dictionary of column name -> value entries.

# In[7]:


for i in range(5):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    #row = {'name':'user_'+str(i), 'age':age, 'is_old':is_old}
    record = Record(name='user_'+str(i), age=age)
    table.insert(record)
table.head()


# ## Select Statements
# Now we show how to select data from the table. Use the `.count()` method to check the number of rows. It also accepts some column conditionals to count entries that satisfy a given criteria

# In[8]:


table.count(), table.count(table['age']>=30)


# Use the `.select()` method with no arguments to retrieve all rows of the table. You can also choose to select one or more columns to select.

# In[9]:


table.select()


# In[10]:


table.select('name')


# In[11]:


table.select(['id','name'])


# In[12]:


table.select(table['age'].sum)


# The SUM() and COUNT() SQL functions have been mapped to `.sum` and `.count` attributes of columns.

# In[13]:


table.select([table['age'].sum,table['age'].count], as_dataclass=False)


# Alternatively, to see the results as a pandas dataframe, we can use ```.select_df()```.

# In[14]:


table.select_df()


# Now we can select specific elements of the db using the ```where``` argument of the ```.select()``` method.

# In[15]:


table.select(where=table['age'] >= 1)


# In[16]:


table.select(where=table['id']==3)


# We can update the results in a similar way, using the ```where``` argument.

# In[17]:


table.update({'name':'smartypants'}, where=table['id']==3)
table.select()


# In[18]:


table.update({'age':table['age']*100})
table.select()


# And we can delete elements using the ```.delete()``` method.

# In[19]:


table.delete(where=table['id']==3)
table.select()


# # Notes on DB Interface
# DocTable2 allows you to access columns through direct subscripting, then relies on the power of sqlalchemy column objects to do most of the work of constructing queries. Here are a few notes on their use. For more demonstration, see the example in examples/dt2_select.ipynb

# In[20]:


# subscript is used to access underlying sqlalchemy column reference (without querying data)
table['id']


# In[21]:


# conditionals are applied directly to the column objects (as we'll see with "where" clause)
table['id'] < 3


# In[22]:


# can also access using .col() method
table.col('id')


# In[23]:


# to access all column objects (only useful for working directly with sql info)
table.columns


# In[24]:


# to access more detailed schema information
table.schema_table()


# In[25]:


# If needed, you can also access the sqlalchemy table object using the .table property.
table.table


# In[26]:


# the count method is also an easy way to count rows in the database
table.count()


# In[27]:


# the print method makes it easy to see the table name and total row count
print(table)

