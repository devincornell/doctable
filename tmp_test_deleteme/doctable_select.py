#!/usr/bin/env python
# coding: utf-8

# # DocTable Examples: Select
# Here I show how to select data from a DocTable. We cover object-oriented conditional selects emulating the `WHERE` SQL clause, as well as some reduce functions.

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

table = doctable.DocTable(target=':memory:', schema=Record, verbose=True)
print(table)


# In[3]:


N = 10
for i in range(N):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    table.insert({'name':'user_'+str(i), 'age':age, 'is_old':is_old}, verbose=False)
print(table)


# ## Regular Selects
# These functions all return lists of ResultProxy objects. As such, they can be accessed using numerical indices or keyword indices. For instance, if one select output row is ```row=(1, 'user_0')``` (after selecting "id" and "user"), it can be accessed such that ```row[0]==row['id']``` and ```row[1]==row['user']```.

# In[4]:


# the limit argument means the result will only return some rows.
# I'll use it for convenience in these examples.
# this selects all rows
table.select(limit=2)


# In[5]:


table.select(['id','name'], limit=1)


# In[6]:


# can also select by accessing the column object (db['id']) itself
# this will be useful later with more complex queries
table.select([table['id'],table['name']], limit=1)


# In[7]:


table.select_first()


# In[8]:


table.select('name',limit=5)


# In[9]:


table.select_first('age')


# ## Conditional Selects

# In[10]:


table.select(where=table['id']==2)


# In[11]:


table.select(where=table['id']<3)


# In[12]:


# mod operator works too
table.select(where=(table['id']%2)==0, limit=2)


# In[13]:


# note parantheses to handle order of ops with overloaded bitwise ops
table.select(where= (table['id']>=2) & (table['id']<=4) & (table['name']!='user_2'))


# In[14]:


table.select(where=table['name'].in_(('user_2','user_3')))


# In[15]:


table.select(where=table['id'].between(2,4))


# In[16]:


# use of logical not operator "~"
table.select(where= ~(table['name'].in_(('user_2','user_3'))) & (table['id'] < 4))


# In[17]:


# more verbose operators .and_, .or_, and .not_ are bound to the doctable package
table.select(where= doctable.or_(doctable.not_(table['id']==4)) & (table['id'] <= 2))


# In[18]:


# now with simple computation
ages = table.select(table['age'])
mean_age = sum(ages)/len(ages)
table.select(table['name'], where=table['age']>mean_age, limit=2)


# In[19]:


# apply .label() method to columns
dict(table.select_first([table['age'].label('myage'), table['name'].label('myname')], as_dataclass=False))


# ## Column Operators
# I bind the .min, .max, .count, .sum, and .mode methods to the column objects. Additionally, I move the .count method to a separate DocTable2 method.

# In[20]:


table.select_first([table['age'].sum, table['age'].count, table['age']], as_dataclass=False)


# In[21]:


# with labels now
dict(table.select_first([table['age'].sum.label('sum'), table['age'].count.label('ct')], as_dataclass=False))


# ## ORDER BY, GROUP BY, LIMIT
# These additional arguments have also been provided.

# In[22]:


# the limit is obvious - it has been used throughout these examples
table.select(limit=2)


# In[23]:


# orderby clause
table.select(orderby=table['age'].desc(), limit=2)


# In[24]:


# compound orderby
table.select(orderby=(table['age'].desc(),table['is_old'].asc()), limit=2)


# In[25]:


# can also use column name directly
# can only use ascending and can use only one col
table.select(orderby='age', limit=2)


# In[26]:


# groupby clause
# returns first row of each group without any aggregation functions
table.select(groupby=table['is_old'])


# In[27]:


# compound groupby (weird example bc name is unique - have only one cat var in this demo)
table.select(groupby=(table['is_old'],table['name']), limit=3)


# In[28]:


# groupby clause using max aggregation function
# gets match age for both old and young groups
table.select(table['age'].max, groupby=table['is_old'])


# ## SQL String Commands and Additional Clauses
# For cases where DocTable2 does not provide a convenient interface, you may submit raw SQL commands. These may be a bit more unwieldly, but they offer maximum flexibility. They may be used either as simply an addition to the WHERE or arbitrary end clauses, or accessed in totality.

# In[29]:


qstr = 'SELECT age,name FROM {} WHERE id=="{}"'.format(table.tabname, 1)
results = table.execute(qstr)
dict(list(results)[0])


# In[30]:


wherestr = 'is_old=="{}"'.format('1')
table.select(wherestr=wherestr, limit=2)


# In[31]:


# combine whrstr with structured query where clause
wherestr = 'is_old=="{}"'.format('1')
table.select(where=table['id']<=5, wherestr=wherestr)


# In[32]:


# combine whrstr with structured query where clause
wherestr = 'is_old=="{}"'.format('1')
table.select(where=table['id']<=5, wherestr=wherestr)


# ## Count Method and Get Next ID
# ```.count()``` is a convenience method. Mostly the same could be accomplished by ```db.select_first(db['id'].count)```, but this requires no reference to a specific column.
# 
# ```.next_id()``` is especially useful if one hopes to enter the id (or any primary key column) into new rows manually. Especially useful because SQL engines don't provide new ids except when a single insert is performed.

# In[33]:


table.count()


# In[34]:


table.count(table['age'] < 0.5)


# ## Select as Pandas Series and DataFrame
# These are especially useful when working with metadata because Pandas provides robust descriptive and plotting features than SQL alone. Good for generating sample information.

# In[35]:


# must provide only a single column
table.select_series(table['age']).head(2)


# In[36]:


table.select_series(table['age']).quantile([0.025, 0.985])


# In[37]:


table.select_df(['id','age']).head(2)


# In[38]:


table.select_df('age').head(2)


# In[39]:


# must provide list of cols (even for one col)
table.select_df([table['id'],table['age']]).corr()


# In[40]:


table.select_df([table['id'],table['age']]).describe().T


# In[41]:


mean_age = table.select_series(table['age']).mean()
df = table.select_df([table['id'],table['age']])
df['old_grp'] = df['age'] > mean_age
df.groupby('old_grp').describe()


# In[42]:


# more complicated groupby aggregation.
# calculates the variance both for entries above and below average age
mean_age = table.select_series(table['age']).mean()
df = table.select_df([table['name'],table['age']])
df['old_grp'] = df['age']>mean_age
df.groupby('old_grp').agg(**{
    'first_name':pd.NamedAgg(column='name', aggfunc='first'),
    'var_age':pd.NamedAgg(column='age', aggfunc=np.var),
})


# # Select with Buffer
# In cases where you have many rows or each row contains a lot of data, you may want to perform a select query which makes requests in chunks. This is performed using the SQL OFFSET command, and querying up to buffsize while yielding each returned row. This system is designed this way because the underlying sql engine buffers all rows retreived from a query, and thus there is no way to stream data into memory without this system.
# 
# NOTE: The limit keyword is incompatible with this method - it will return all results. A workaround is to use the approx_max_rows param, which will return at minimum this number of rows, at max the specified number of rows plus buffsize.

# In[43]:


for row_chunk in table.select_chunks(chunksize=2, where=(table['id']%2)==0, verbose=False):
    print(row_chunk)

