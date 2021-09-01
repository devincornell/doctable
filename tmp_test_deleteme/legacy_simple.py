#!/usr/bin/env python
# coding: utf-8

# # DocTable Simple Example
# In this notebook, I show how to define a DocTable as a python class, populate the DocTable using the .add() and .addmany() commands, query data through generators and pandas dataframes, and finally update DocTable entries.

# In[1]:


from pprint import pprint
from timeit import default_timer as timer
from dt1_helper import get_sklearn_newsgroups

import sys
sys.path.append('..')
import doctable as dt # this will be the table object we use to interact with our database.


# ## Get News Data From sklearn.datasets
# Then parses into a dataframe.

# In[2]:


ddf = get_sklearn_newsgroups()
print(ddf.info())
ddf.head(3)


# ## Define DocTable Class
# This class definition will contain the columns, datatypes, unique constraints, and index commands needed for your DocTable.
# In moving your data from DataFrame to DocTable, you should consider column data types and custom indices carefully.

# In[4]:


# this class will represent the doctable. It inherits from DocTable a number of add/query/remove functions.
# of course, you can add any additional methods to this class definition as you find useful.
class SimpleNewsGroups(dt.DocTable):
    def __init__(self, fname):
        '''
            This includes examples of init variables. See DocTable class for complete list of options.
            Inputs:
                fname: fname is the name of the new sqlite database that will be used for this class.
        '''
        tabname = 'simplenewsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema=(
                'id integer primary key autoincrement',
                'file_id int',
                'category string',
                'raw_text string',
            )
        )
        
        # this section defines any other commands that should be executed upon init
        # NOTICE: references tabname defined in the above __init__ function
        # extra commands to create index tables for fast lookup
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")


# Create a connection to the database by constructing an instance of the class. If this is the first time you've run this code, it will create a new sqlite database file with no entries.

# In[5]:


sng = SimpleNewsGroups('simple_news_group.db')
print(sng)


# ## Adding Data
# There are two common ways to add data to your DocTable.
# 
# (1) Add in rows individually
# 
# (2) Add in bulk with or without specifying column names

# In[6]:


# adds data one row at a time. Takes longer than bulk version
start = timer()

for ind,dat in ddf.iterrows():
    row = {'file_id':int(dat['filename']), 'category':dat['target'], 'raw_text':dat['text']}
    sng.add(row, ifnotunique='replace')

print((timer() - start)*1000, 'mil sec.')
print(sng)


# In[7]:


# adds tuple data in bulk by specifying columns we are adding
start = timer()

col_order = ('file_id','category','raw_text')
data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
sng.addmany(data,keys=col_order, ifnotunique='replace')

print((timer() - start)*1000, 'mil sec.')
print(sng)


# ## Querying Data
# There are two primary ways of querying data from a DocTable:
# 
# (1) retrieve one-by-one from generator using ".get()" function.
# (2) retrieve all data in Pandas DataFrame suing ".getdf()" function.

# In[8]:


result = sng.get(
    sel=('file_id','raw_text'), 
    where='category == "rec.motorcycles"', 
    orderby='file_id ASC', 
    limit=3,
)
for row in result:
    print(str(row['file_id'])+':', row['raw_text'][:50])


# In[9]:


result_df = sng.getdf(
    sel=('file_id','raw_text'), 
    where='category == "rec.motorcycles"', 
    orderby='file_id ASC', 
    limit=5,
)
result_df


# ## Updating Data in DocTable
# The ".update()" function will change entries in the DocTable.

# In[10]:


sng.update({'category':'nevermind',},where='file_id == "103121"')
sng.getdf(where='file_id == "103121"') # to see update, look at "category" column entry

