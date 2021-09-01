#!/usr/bin/env python
# coding: utf-8

# # ParseTreeDoc Column Types
# Creating parsetrees with spacy can be a computationally expensive task, so we may often want to store them in a database for better use. Because they may be large binary files, we will store them as pickle file column types, but with an additional serialization step.

# In[1]:


import spacy
nlp = spacy.load('en_core_web_sm')
import numpy as np
from pathlib import Path

import sys
sys.path.append('..')
import doctable

# automatically clean up temp folder after python ends
tmpfolder = doctable.TempFolder('tmp')


# Create some test data and make a new `ParseTreeDoc` object.

# In[2]:


texts = [
    'Help me Obi-Wan Kenobi. You’re my only hope. ',
    'I find your lack of faith disturbing. ',
    'Do, or do not. There is no try. '
]
parser = doctable.ParsePipeline([nlp, doctable.Comp('get_parsetrees')])
docs = parser.parsemany(texts)
for doc in docs:
    print(len(doc))


# Now we create a schema that includes the `doc` column and the `ParseTreeFileCol` default value. Notice that using the type hint `ParseTreeDoc` and giving a generic `Col` default value is also sufficient.

# In[3]:


import dataclasses
@dataclasses.dataclass
class DocRow(doctable.DocTableRow):
    id: int = doctable.IDCol()
    doc: doctable.ParseTreeDoc = doctable.ParseTreeFileCol('tmp/parsetree_pickle_files')
        
    # could also use this:
    #doc: doctable.ParseTreeDoc = doctable.Col(type_args=dict(folder='tmp/parsetree_pickle_files'))
    
db = doctable.DocTable(target='tmp/test_ptrees.db', schema=DocRow, new_db=True)
db.schema_info()


# In[4]:


#db.insert([{'doc':doc} for doc in docs])
for doc in docs:
    db.insert({'doc': doc})
db.head(3)


# In[5]:


for idx, doc in db.select(as_dataclass=False):
    print(f"doc id {idx}:")
    for i, sent in enumerate(doc):
        print(f"\tsent {i}: {[t.text for t in sent]}")


# See that the files exist, and we can remove/clean them just as any other file column type.

# In[6]:


for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))


# In[7]:


db.delete(db['id']==1)
for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))
db.head()


# In[8]:


db.clean_col_files('doc')
for fpath in tmpfolder.path.rglob('*.pic'):
    print(str(fpath))

