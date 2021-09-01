#!/usr/bin/env python
# coding: utf-8

# # DocTable File Column Types
# It is often good advice to avoid storing large binary data in an SQL table because it will significantly impact the read performance of the entire table. I find, however, that it can be extremely useful in text analysis applications as a way to keep track of a large number of models with associated metadata. As an alternative to storing binary data in the table directly, `DocTable` includes a number of custom column types that can transparently store data into the filesystem and keep track of it using the schema definitions.
# 
# I provide two file storage column types: (1) `TextFileCol` for storing text data, and (2) `PickleFileCol` for storing any python data that requires pickling.

# In[1]:


import numpy as np
from pathlib import Path

import sys
sys.path.append('..')
import doctable

# automatically clean up temp folder after python ends
tmpfolder = doctable.TempFolder('tmp')


# Now I create a new table representing a matrix. Notice that I use the `PickleFileCol` column shortcut to create the column. This column is equivalent to `Col(None, coltype='picklefile', type_args=dict(folder=folder))`. See that to SQLite, this column simply looks like a text column.

# In[2]:


import dataclasses
@doctable.schema(require_slots=False)
class MatrixRow:
    id: int = doctable.IDCol()
    array: np.ndarray = doctable.PickleFileCol('tmp/matrix_pickle_files') # will store files in the tmp directory
    
db = doctable.DocTable(target='tmp/test.db', schema=MatrixRow, new_db=True)
db.schema_info()


# Now we insert a new array. It appears to be inserted the same as any other object. 

# In[3]:


db.insert({'array': np.random.rand(10,10)})
db.insert({'array': np.random.rand(10,10)})
print(db.count())
db.select_df(limit=3)


# But when we actually look at the filesystem, we see that files have been created to store the array.

# In[4]:


for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))


# If we want to see the raw data stored in the table, we can create a new doctable without a defined schema. See that the raw filenames have been stored in the database. Recall that the directory indicating where to find these files was provided in the schema itself. 

# In[5]:


vdb = doctable.DocTable('tmp/test.db')
print(vdb.count())
vdb.head()


# ## Data Folder Consistency
# Now we try to delete a row from the database. We can see that it was deleted as expected.

# In[6]:


db.delete(where=db['id']==1)
print(db.count())
db.head()


# However, when we check the folder where the data was stored, we find that the file was, in fact, not deleted. This is the case for technical reasons.

# In[7]:


for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))


# We can clean up the unused files using `clean_col_files()` though. Note that the specific column to clean must be provided.

# In[8]:


db.clean_col_files('array')
for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))


# There may be a situation where doctable cannot find the folder associated with an existing row. We can also use `clean_col_files()` to check for missing data. This might most frequently occur when the wrong folder is specified in the schema after moving the data file folder. For example, we delete all the pickle files in the directory and then run `clean_col_files()`.

# In[9]:


[fp.unlink() for fp in tmpfolder.path.rglob('*.pic')]
for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))


# In[10]:


# see that the exception was raised
try:
    db.clean_col_files('array')
except FileNotFoundError as e:
    print(e)


# ## Text File Types
# We can also store text files in a similar way. For this, use `TextFileCol` in the folder specification.

# In[11]:


@dataclasses.dataclass
class TextFileRow(doctable.DocTableRow):
    id: int = doctable.IDCol()
    text: str = doctable.TextFileCol('tmp/my_text_files') # will store files in the tmp directory
    
tdb = doctable.DocTable(target='tmp/test_textfiles.db', schema=TextFileRow, new_db=True)
tdb.insert({'text': 'Hello world. DocTable is the most useful python package of all time.'})
tdb.insert({'text': 'Star Wars is my favorite movie.'})
tdb.head()


# In[12]:


# and they look like text files
vdb = doctable.DocTable('tmp/test_textfiles.db')
print(vdb.count())
vdb.head()


# See that the text files were created, and they look like normal text files so we can read them normally.

# In[13]:


for fpath in tmpfolder.path.rglob('*.txt'):
    print(f"{fpath}: {fpath.read_text()}")


# In[ ]:





# In[ ]:




