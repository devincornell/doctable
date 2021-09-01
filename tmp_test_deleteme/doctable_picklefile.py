#!/usr/bin/env python
# coding: utf-8

# # DocTable Example: Pickle and Text Files
# Here I show a bit about how to use `picklefile` and `textfile` column types. DocTable transparently handles saving and reading column data as separate files when data is large to improve performance of select queries. It will automatically create a folder in the same directory as your sqlite database and save or read file data as if you were working with a regular table entry.

# In[1]:


import os
import sys
sys.path.append('..')
import doctable


# In[2]:


tmp = doctable.TempFolder('./tmp') # will delete folder upon destruction

# create column schema: each row corresponds to a pickle
import dataclasses
@doctable.schema(require_slots=False)
class FileEntry:
    pic: list = doctable.Col(coltype='picklefile', type_args=dict(folder=tmp.path))
    idx: int = doctable.IDCol()
    
db = doctable.DocTable(schema=FileEntry, target=':memory:')


# First we try inserting a basic object, where the data will be stored in a pickle file. We can see from the `select` statement that the data read/write is handled transparently by doctable.

# In[3]:


a = [1, 2, 3, 4, 5]
db.insert(FileEntry(a))
db.select() # regular select using the picklefile datatype


# We can also try turning off the transparent conversion, and instead retrieve the regular directory.

# In[4]:


with db['pic'].type.control:
    r = db.select()
r


# For performance reasons, DocTable never deletes stored file data unless you call the `.clean_col_files()` method directly. It will raise an exception if a referenced file is missing, and delete all files which are not referenced in the table. This is a costly function call, but a good way to make sure your database is 1-1 matched with your filesystem.

# In[5]:


# deletes files not in db and raise error if some db files not in filesystem
db.clean_col_files('pic')


# Now I create another DocTable with a changed `fpath` argument. Because the argument changed, DocTable will raise an exception when selecting or calling `.clean_col_files()`. Be wary of this!

# In[6]:


tmp.rmtree()

