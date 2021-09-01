#!/usr/bin/env python
# coding: utf-8

# # Example: Multiple Tables
# In this example, I show how doctable can be used with multiple inter-related tables to perform queries which automatically merge different aspects of your dataset when you use `.select()`. By integrating these relations into the schema, your database can automatically maintain consistency between tables by deleting irrelevant elements when their relations disappear. There are two important features of any multi-table schema using doctable:
# 
# (1) Set the foreign_keys=True in the original doctable or ConnectEngine constructor. Otherwise sqlalchemy will not enable.
# 
# (2) Use the "foreignkey" column type to set the constraint, probably with the onupdate and ondelete keywords specifiied.
# 
# In this example I'll create interrelated tables for authors and their books.

# In[1]:


import sys
sys.path.append('..')
import doctable


# In[2]:


class Authors(doctable.DocTable):
    _tabname_ = 'authors'
    _schema_ = (
        ('idcol', 'id'),
        ('string', 'name', dict(unique=True)),
        ('string', 'fav_color'),
        ('date_updated', 'updated'),
    )
adb = Authors(target=':memory:', foreign_keys=True)
#adb.execute('pragma foreign_keys=ON')
adb


# In[3]:


class Books(doctable.DocTable):
    _tabname_ = 'books'
    _schema_ = (
        ('idcol', 'id'), # each book has its own id
        ('string', 'title'),
        
        # reference to authors table
        ('integer', 'authname'), 
        ('foreignkey', 'authname', 'authors.name', dict(onupdate="CASCADE", ondelete="CASCADE")),
        
        # make unique combination
        ('index', 'ind_authtitle', ['title', 'authname'], dict(unique=True)),
    )
bdb = Books(engine=adb.engine)
bdb


# In[4]:


# see that both are registered with the engine metadata
adb.engine.tables.keys()


# In[5]:


# define a test dataset
collection = (
    ('Devin Cornell', 'green', 'The Case of Austerity'),
    ('Devin Cornell', 'green', 'Gender Stereotypes'),
    ('Devin Cornell', 'green', 'Colombian Politics'),
    ('Pierre Bourdieu', 'orange', 'Distinction'),
    ('Pierre Bourdieu', 'orange', 'Symbolic Power'),
    ('Jean-Luc Picard', 'red', 'Enterprise Stories'),
)


# In[6]:


for auth, color, title in collection:
    adb.insert({'name':auth, 'fav_color': color}, ifnotunique='ignore')
    bdb.insert({'authname':auth, 'title': title}, ifnotunique='ignore')
adb.count(), bdb.count()


# In[7]:


adb.head()


# In[8]:


bdb.head(10)


# ## Joint Select Statements
# You can perform joins by using select queries with column objects from different tables.

# In[9]:


# this is a left join
bdb.select(['title', adb['name'], adb['fav_color']], where=bdb['authname']==adb['name'])


# In[10]:


# with tables reversed, still returns same output
adb.select(['name', bdb['title']], where=adb['name']==bdb['authname'])


# ## Cascade deletion
# See now that by deleting the author "Devin Cornell", we also removed the corresponding rows in the book table.

# In[12]:


adb.delete(where=adb['name']=='Devin Cornell')


# In[13]:


adb.head()


# In[14]:


bdb.head(10)

