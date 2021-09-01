#!/usr/bin/env python
# coding: utf-8

# # Manage SQL Connections with DocTable
# This is meant to give a bit more depth describing how doctable works under-the-hood. I won't cover the details of DocTable methods or working with doctable objects, but I will try to give a clearer sense of how connections and tables are managed within a doctable instance.
# 
# The driving motivator behind doctable is to create an object-oriented interface for working with sql tables by linking schemas described in your code with the structure of the databases you work with. This model is less ideal for the kinds of application-based frameworks where you would define the database schema once and build code around it separately, but works well for data science applications where you will be creating new tables and playing with different schemas regularly as your approach and end-goals change.
# 
# When you instantiate a DocTable (or inheriting class), the object will convert your provided schema into a set of sqlalchemy objects which are then stored in-memory as part of the doctable instance. If the table does not already exist in the actual database, DocTable can create one that matches the provided schema, and then the schema will be used to work with the underlying database table. I will now discuss the lower-level objects that manage the metadata and connections to the database.

# In[1]:


import sys
sys.path.append('..')
import doctable


# ## ConnectEngine Class
# Each doctable maintains a `ConnectEngine` object to manage database connections and metadata that make all other database operations possible. I'll demonstrate how to instantiate this class manually to show how it works.
# 
# The constructor takes arguments for dialect (sqlite, mysql, etc) and database target (filename or database server) to create new sqlalchemy [engine](https://docs.sqlalchemy.org/en/13/core/engines_connections.html) and [metadata](https://docs.sqlalchemy.org/en/13/faq/metadata_schema.html) objects. The engine object stores information about the target and can generate database connections, the metadata object stores schemas for registered tables. To work with a table, the metadata object must have the table schema registered, although it can be constructed from the database object itself.
# 
# See here that the constructor requires a target (file or server where the database is located) and a dialect (flavor of database engine). This connection sits above individual table connections, and thus maintains no connections of it's own - only the engine that can create connections. We can, however list the tables in the database and perform other operations on the table.

# In[2]:


engine = doctable.ConnectEngine(target=':memory:', dialect='sqlite')
engine


# ### Working with tables
# You can also execute connectionless queries directly from this object, although normally you would create a connection object first and then execute queries from the connection. In this example I use a custom sql query to create a new table.
# 
# As the ConnectEngine sits above the level of tables, we can list and drop tables from here.

# In[3]:


# see there are no tables here yet.
engine.list_tables()


# In[4]:


# run this raw sql query just for example
# NOTE: Normally you would NOT create a table this way using doctable.
# This is just for example purposes.
query = 'CREATE TABLE temp (id INTEGER PRIMARY KEY, number INTEGER NOT NULL)'
engine.execute(query)


# In[5]:


# see that the table is now in the database
engine.list_tables()


# In[6]:


# uses inspect to ask the database directly for the schema
engine.schema('temp')


# In[7]:


# or as a dataframe
engine.schema_df('temp')


# All of these methods I've shown so far access the database tables directly, but currently our python objects do not have any idea of what the table schema looks like. You can view the sqlalchemy table objects actually registered with the engine by using the .tables property. See that it is currently empty! Our python code is not able to work with the table using objects because it does not have record of the schema. Now we'll show how to register tables with the engine.
# 
# ### Creating and accessing tables
# To create a data structure internally representing the database structure, we can either ask sqlalchemy to read the database and create the schema, or we can provide lists of sqlalchemy column objects. Wee that we can access the registered tables using the .tables property.

# In[8]:


# see that currently our engine does not have information about the table we created above.
engine.tables


# In[9]:


# now I ask doctable to read the database schema and register the table in metadata.
engine.add_table('temp')


# In[10]:


# and we can see that the table is registered
engine.tables


# When add_table() is called, a new sqlalchemy.Table object is registered in the engine's metadata and returned. If add_table() is called again, it will return the table already registered in the metadata. Because we usually use doctable to manage tables, we'll just show a short example here.

# In[11]:


# while we can use doctable to do most of this work 
#  usually, I'll just show how sqlalchemy core objects 
#  can be used to create a table in ConnectEngine.
from sqlalchemy import Column, Integer, String

# create a list of columns
columns = (
    Column('id', Integer, primary_key = True), 
    Column('name', String), 
)

# we similarly use the add_table() method to store the schema
#  in the metadata
engine.add_table('temp2', columns=columns)


# In[12]:


# see now that the engine has information about both tables
engine.tables


# In[13]:


# and see that you can get individual table object references like this
engine.tables['temp']


# ### Dropping tables
# Dropping tables is simple enough, but remember that the schema stored in the database and the objects in code mirror each other, so it is best to manipulate them at the same time. Use .drop_table instead of issuing CREATE TABLE query to make sure they stay in sync. The method can also be used on tables that are not in the metadata engine.

# In[14]:


# by providing the argument as a string
engine.drop_table('temp')


# In[15]:


engine.list_tables()


# In cases where an underlying table has been deleted but metadata is retained, the drop_table() method will still work but you may need to call clear_metadata() to flush all metadata and add_all_tables() to re-create the metadata from the actual data.

# In[16]:


# see this works although the temp3 table is not registered in engine metadata
query = 'CREATE TABLE temp3 (id INTEGER PRIMARY KEY, number INTEGER NOT NULL)'
engine.execute(query)
engine.drop_table('temp3')


# In[17]:


# this will delete the underlying table even though the metadata information still exists.
query = 'CREATE TABLE temp4 (id INTEGER PRIMARY KEY, number INTEGER NOT NULL)'
engine.execute(query)
engine.execute(f'DROP TABLE IF EXISTS temp4')
engine.list_tables()


# In[18]:


# see that the table is still registered in the metadata
engine.tables


# In[19]:


# in this case, it might be simplest just to clear all metadata
# and re-build according to exising tables
engine.clear_metadata()
engine.add_existing_tables()
engine.tables


# ## Managing connections with ConnectEngine
# ConnectEngine objects are used to create database connections which are maintained by individual doctable objects. Use the get_connection() function to retreive a new connection object which you can use to execute queries. While garbage collecting the connection objects will close the individual connection, sometimes all connections need to be closed simultaneously. This is especially important because garbage-collecting the ConnectEngine object doesn't mean the connections will be garbage-collected if they have references elsewhere in your code. You can close all connections using the close_connections() method.

# In[20]:


# make new connection
conn = engine.connect()
conn


# In[21]:


# see here we just run a select query on the empty table, returning an empty list
list(conn.execute('SELECT * FROM temp2'))


# In[22]:


engine.close_connections() # closes all connections in the pool


# An important use-case of this feature is when you have multiple processes accessing the same database. In general, each process should have separate connections to the database, but both the engine and metadata stored with the ConnectEngine can be copied. Here I'll show a basic multiprocessing case using the Distribute class (it works much like multiprocessing.Pool()).
# 
# In using the map function we open two processes, and in the thread function we call the close_connections() method to delete existing connections which don't exist in this new memory space.

# In[23]:


def thread(nums, engine):
    # close connections that were opened in other thread
    engine.close_connections()
    
    # create a new connection for this thread
    thread_conn = engine.get_connection()

numbers = [1,2]
with doctable.Distribute(2) as d:
    d.map(thread, numbers, engine)


# In[24]:


engine.list_tables()


# ## DocTable and ConnectEngine
# Every DocTable object maintains a ConnectEngine to store information about the table they represent, and can be accessed through the engine property. When a target and dialect are provided to doctable, it will automatically initialize a new ConnectEngine and store a new connection object.

# In[25]:


# create a new doctable and view it's engine
schema = (('idcol', 'id'), ('string', 'name'))
db = doctable.DocTable(target=':memory:', schema=schema)
str(db.engine)


# The DocTable constructor can also accept an engine in place of a target and dialect, and thus share ConnectEngines between multiple DocTable objects. In this case, the doctable constructor will use the provided schema to insert the table information into the engine metadata and create the table if doesn't already exist. It will also generate a new connection object from the ConnectEngine.

# In[26]:


# a w
engine.clear_metadata()
print(engine.tables.keys())
print(engine.list_tables())


# In[27]:


# make a new doctable using the existing engine
schema = (('idcol', 'id'), ('string', 'name'))
db = doctable.DocTable(engine=engine, schema=schema, tabname='tmp5')
db


# In[28]:


# make another doctable using existing engine
schema2 = (('idcol', 'id'), ('string', 'name'))
db2 = doctable.DocTable(engine=engine, schema=schema2, tabname='tmp6')
db2


# In[29]:


# we can see that both tables have been created in the database
engine.list_tables()


# In[30]:


# and that both are registered in the metadata
engine.tables.keys()


# Some ConnectEngine methods are also accessable through the DocTable instances.

# In[31]:


db.list_tables()


# In[32]:


db.schema_table()


# In[33]:


# and this is equivalent to calling the engine method reopen(), which clears 
#  metadata and closes connection pool
db.reopen_engine()

