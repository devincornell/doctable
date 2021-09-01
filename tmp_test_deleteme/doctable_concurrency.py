#!/usr/bin/env python
# coding: utf-8

# # Concurrent Database Connections
# DocTable makes it easy to establish concurrent database connections from different processes. DocTable objects can be copied as-is from one process to another, except that you must call `.reopen_engine()` to initialize in process thread. This removes now stale database connections (which are _not_ meant to traverse processes) from the engine connection pool.
# 
# You may also want to use a large timeout using the timeout argument of the doctable constructor (provided in seconds).

# In[1]:


import sqlalchemy
from multiprocessing import Process
import os
import random
import string
import dataclasses
import time
import sys
sys.path.append('..')
import doctable


# In[2]:


import datetime
@doctable.schema
class SimpleRow:
    __slots__ = []
    id: int = doctable.IDCol()
    updated: datetime.datetime = doctable.AddedCol()
    process: str = doctable.Col()
    number: int = doctable.Col()

tmp = doctable.TempFolder('exdb')
db = doctable.DocTable(schema=SimpleRow, target=tmp.joinpath('tmp_concurrent.db'), new_db=True, timeout=60)


# In[3]:


def thread_func(numbers, db):
    process_id = ''.join(random.choices(string.ascii_uppercase, k=2))
    print(f'starting process {process_id}')
    db.reopen_engine() # create all new connections
    for num in numbers:
        db.insert({'process': process_id, 'number': num})
        time.sleep(0.01)

numbers = list(range(100)) # these numbers are to be inserted into the database
        
db.delete()
with doctable.Distribute(5) as d:
    d.map_chunk(thread_func, numbers, db)
db.head(10)


# ## Using `QueueInserter` to queue rows for insertion
# Because processes must wait on one another for insertions, it may be desirable to insert databases in bulk. To avoid adding additional queueing logic to your code, you can use the builtin QueueInserter object, retreived from a DocTable using `get_queueinserter()`. Set the `chunk_size` param to determine the size of each insertion.

# In[4]:


inserter = db.get_queueinserter(chunk_size=2, verbose=True)

db.delete()
for i in range(5):
    inserter.insert({'number': i})

inserter.dump() # dump remaining rows into db (happens automatically upon garbage collection)
db.head(10)


# ## `QueueInserter` example in threads
# We can also create `QueueInserter` objects in threads and observe that they are inserted simulataneously.

# In[7]:


def thread_func(numbers, db):
    process_id = ''.join(random.choices(string.ascii_uppercase, k=2))
    print(f'starting process {process_id}')
    db.reopen_engine() # create all new connections
    inserter = db.get_queueinserter(chunk_size=2)
    for num in numbers:
        inserter.insert({'process': process_id, 'number': num})
        time.sleep(0.01)

numbers = list(range(100)) # these numbers are to be inserted into the database
        
db.delete()
with doctable.Distribute(3) as d:
    d.map_chunk(thread_func, numbers, db)
db.head(10)


# In[ ]:





# In[ ]:




