#!/usr/bin/env python
# coding: utf-8

# # DocTable Example: Schemas
# In this example, we show column specifications for each available type, as well as the [sqlalchemy equivalents](https://docs.sqlalchemy.org/en/13/core/type_basics.html) on which they were based. Note that .
# 
# Each column in the schema passed to doctable is a 2+ tuple containing, in order, the column type, name, and arguments, and optionally the sqlalchemy type arguemnts.

# In[1]:


from datetime import datetime
from pprint import pprint
import pandas as pd
import typing

import sys
sys.path.append('..')
import doctable


# In[11]:


@doctable.schema
class MyClass:
    __slots__ = []
    # builtin column types
    idx: int = doctable.IDCol()
        
    # unique name
    name: str = doctable.Col(unique=True) # want to be the first ordered argument

    
    # special columns for added and updated
    updated: datetime = doctable.UpdatedCol()
    added: datetime = doctable.AddedCol()

    # custom column types 
    lon: float = doctable.Col()
    lat: float = doctable.Col()

    # use Col to use factory to construct emtpy list
    # will be stored as binary/pickle type, since no other available
    elements: typing.Iterable = doctable.Col(list) 
    
class MyTable(doctable.DocTable):
    _schema_ = MyClass
    # indices and constraints
    _indices_ = {
        'lonlat_index': ('lon', 'lat', {'unique':True}),
        'name_index': ('name',),
    }
    _constraints_ = (
        ('check', 'lon > 0', {'name':'check_lon'}), 
        ('check', 'lat > 0'), 
        #('foreignkey', ('a','b'), ('c','d'))
    )
md = MyTable(target=':memory:', verbose=True)
#pprint(md.schemainfo)
pd.DataFrame(md.schema_info())


# In[ ]:




