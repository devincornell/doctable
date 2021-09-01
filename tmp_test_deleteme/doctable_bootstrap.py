#!/usr/bin/env python
# coding: utf-8

# # Document Bootstrapping Examples
# When estimating machine learning or statistical models on your corpus, you may need to bootstrap documents (randomly sample with replacement). The `.bootstrap()` method of `DocTable` will act like a select statement but return a bootstrap object instead of a direct query result. Here I show how to do some basic bootstrapping using an example doctable.

# In[1]:


import random
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
import doctable as dt


# ### Create Example DocTable
# First we define a DocTable that will be used for examples.

# In[2]:


schema = (
    ('integer','id',dict(primary_key=True, autoincrement=True)),
    ('string','name', dict(nullable=False, unique=True)),
    ('integer','age'),
    ('boolean', 'is_old'),
)
db = dt.DocTable(target=':memory:', schema=schema)
print(db)


# Then we add several example rows to the doctable.

# In[3]:


for i in range(10):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    row = {'name':'user_'+str(i), 'age':age, 'is_old':is_old}
    db.insert(row, ifnotunique='replace')

for doc in db.select(limit=3):
    print(doc)


# ### Create a Bootstrap
# We can use the doctable method `.bootstrap()` to return a bootstrap object using the keyword argument `n` to set the sample size (will use number of docs by default). This method acts like a select query, so we can specify columns and use the where argument to choose columns and rows to be bootstrapped. The bootsrap object contains the rows in the `.doc` property.
# 
# Notice that while our select statement drew three documens, the sample size specified with `n` is 5. The boostrap object will always return 5 objects, even though the number of docs stays the same.

# In[4]:


bs = db.bootstrap(['name','age'], where=db['id'] % 3 == 0, n=4)
print(type(bs))
print(len(bs.docs))
bs.n


# Use the bootstrap object as an iterator to access the bootstrapped docs. The bootstrap object draws a sample upon instantiation, so the same sample is maintained until reset.

# In[5]:


print('first run:')
for doc in bs:
    print(doc)
print('second run:')
for doc in bs:
    print(doc)


# ### Draw New Sample
# You can reset the internal sample of the bootstrap object using the `.set_new_sample()` method. See that we now sample 2 docs and the output is different from previous runs. The sample will still remain the same each time we iterate until we reset the sample.

# In[6]:


bs.set_new_sample(2)
print('first run:')
for doc in bs:
    print(doc)
print('second run:')
for doc in bs:
    print(doc)


# And we can iterate through a new sample using `.new_sample()`. Equivalent to calling `.set_new_sample()` and then iterating through elements.

# In[7]:


print('drawing new sample:')
for doc in bs.new_sample(3):
    print(doc)
print('repeating sample:')
for doc in bs:
    print(doc)


# I may add additional functionality in the future if I use this in any projects, but that's it for now.
