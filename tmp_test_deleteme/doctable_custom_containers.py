#!/usr/bin/env python
# coding: utf-8

# # Custom Containers from Select Queries
# Here I show how to use custom containers to wrap results from select queries. This may be useful if you intend to build an aggregate data structure from resulting rows.

# In[1]:


import sys
sys.path.append('..')
import doctable


# We start by creating a schema for our database and using it to create a new doctable object. This schema includes three columns, and we insert some elements into the table for testing.

# In[2]:


import dataclasses
import datetime
@doctable.schema(require_slots=False)
class Row:
    number: int
    idx: int = doctable.IDCol()
    updated: datetime.datetime = doctable.UpdatedCol()

db = doctable.DocTable(schema=Row, target=':memory:')
db.insert([Row(i) for i in range(10000)])
db.count()


# You can see that by default, the return type is a list.

# In[3]:


type(db.select())


# Using the `result_container` parameter of `.select()`, we are able to use a custom class to wrap our data. First I show an example using `RowList`, a class which extends the basic python `list`, adding only a simple method to return the sum of numbers associated with each row.

# In[4]:


class RowList(list):
    def payload_sum(self):
        return sum(r.number for r in self)
    
res = db.select(result_container=RowList)
print(f'type={type(res)}, len={len(res)}, sum={res.payload_sum()}')


# We can use any class that takes a set of results as the single argument in the constructor. I now define a class `RowGroup` that separates out rows with big and little numbers. When I providee `RowGroup` to the `result_container` argument of the select query, we can see that the RowGroup has separated out the rows into the two groups.

# In[ ]:


class RowGroup:
    def __init__(self, rows):
        self.big = list()
        self.little = list()
        for row in rows:
            if row.number > 100:
                self.big.append(row)
            else:
                self.little.append(row)

res = db.select(result_container=RowGroup)
print(f'type={type(res)}, big len={len(res.big)}, little len={len(res.little)}')


# Here I showed how we can create custom containers for our row objects. Of course, we can create new methods that use select with the `result_container` argument to return the RowList.

# In[ ]:


class MyTable(doctable.DocTable):
    def select_rowlist(self, *args, **kwargs):
        return super().select(*args, result_container=RowList, **kwargs)

db2 = MyTable(schema=Row, target=':memory:')
db2.insert([Row(i) for i in range(10000)])
res = db2.select_rowlist()
print(f'type={type(res)}, len={len(res)}, sum={res.payload_sum()}')

