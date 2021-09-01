#!/usr/bin/env python
# coding: utf-8

# # DocTable Examples: Update
# Here I show how to update data into a DocTable. In addition to providing updated values, DocTable also allows you to create map functions to transform existing data.

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
        
def new_db():
    table = doctable.DocTable(schema=Record, target=':memory:', verbose=True)
    N = 10
    for i in range(N):
        age = random.random() # number in [0,1]
        is_old = age > 0.5
        table.insert({'name':'user_'+str(i), 'age':age, 'is_old':is_old}, verbose=False)
    return table

table = new_db()
print(table)


# In[3]:


table.select_df(limit=3)


# ## Single Update
# Update multiple (or single) rows with same values.

# In[4]:


table = new_db()
table.select_df(where=db['is_old']==True, limit=3, verbose=False)


# In[ ]:


table = new_db()
table.update({'age':1},where=table['is_old']==True)
table.update({'age':0},where=table['is_old']==False)
table.select_df(limit=3, verbose=False)


# ## Apply as Map Function
# This feature allows you to update columns based on the values of old columns.

# In[ ]:


table = new_db()
values = {table['name']:table['name']+'th', table['age']:table['age']+1, table['is_old']:True}
table.update(values)
table.select_df(limit=3, verbose=False)


# ## Apply as Set of Ordered Map Functions
# This is useful for when the updating of one column might change the value of another, depending on the order in which it was applied.

# In[ ]:


table = new_db()
values = [(table['name'],table['age']-1), (table['age'],table['age']+1),]
table.update(values)
table.select_df(limit=3, verbose=False)


# ## Update Using SQL WHERE String

# In[ ]:


table = new_db()
table.update({'age':1.00}, wherestr='is_old==true')
table.select_df(limit=5, verbose=False)

