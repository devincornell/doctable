#!/usr/bin/env python
# coding: utf-8

# # DocTable Examples: Insert and Delete
# Here we show basics of inserting and deleting data into a doctable.

# In[1]:


import random
import pandas as pd
import numpy as np

import sys
sys.path.append('..')
import doctable


# In[2]:


import dataclasses
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col(nullable=False)
    age: int = None
    is_old: bool = None


# In[3]:


def make_rows(N=3):
    rows = list()
    for i in range(N):
        age = random.random() # number in [0,1]
        is_old = age > 0.5
        yield {'name':'user_'+str(i), 'age':age, 'is_old':is_old}
    return rows


# # Basic Inserts
# There are only two ways to insert: one at a time (pass single dict), or multiple at a time (pass sequence of dicts).

# In[4]:


table = doctable.DocTable(target=':memory:', schema=Record, verbose=True)
for row in make_rows():
    table.insert(row)
table.select_df()


# In[5]:


newrows = list(make_rows())
table.insert(newrows)
table.select_df(verbose=False)


# ## Deletes

# In[6]:


# delete all entries where is_old is false
table.delete(where=~table['is_old'])
table.select_df(verbose=False)


# In[7]:


# use vacuum to free unused space now
table.delete(where=~table['is_old'], vacuum=True)
table.select_df(verbose=False)


# In[8]:


# delete everything
table.delete()
table.count()

