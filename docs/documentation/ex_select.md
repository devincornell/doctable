# Select Queries with `doctable`

In this document I will describe the interface for performing select queries with `doctable`. 


```python

import pandas as pd
import numpy as np
import typing

import sys
sys.path.append('..')
import doctable
```

#### Define a demonstration schema

The very first step is to define a table schema that will be appropriate for our examples. This table includes the typical `id` column (the first column, specified by `order=0`), as well as string, integer, and boolean attributes. The object used to specify the schema is called a _container_, and I will use that terminology as we go.


```python
@doctable.table_schema
class Record:
    name: str = doctable.Column(column_args=doctable.ColumnArgs(nullable=False, unique=True))
    age: int = doctable.Column()
    is_old: bool = doctable.Column()
    
    id: int = doctable.Column(
        column_args=doctable.ColumnArgs(
            order = 0, 
            primary_key=True, 
            autoincrement=True
        ),
    )

core = doctable.ConnectCore.open(target=':memory:', dialect='sqlite', echo=True)

with core.begin_ddl() as ddl:
    rtab = ddl.create_table_if_not_exists(container_type=Record)
```

    2023-11-13 08:38:32,059 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,060 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("Record")
    2023-11-13 08:38:32,060 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-13 08:38:32,061 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("Record")
    2023-11-13 08:38:32,062 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-13 08:38:32,063 INFO sqlalchemy.engine.Engine 
    CREATE TABLE "Record" (
    	id INTEGER, 
    	age INTEGER, 
    	is_old INTEGER, 
    	name VARCHAR NOT NULL, 
    	PRIMARY KEY (id), 
    	UNIQUE (name)
    )
    
    
    2023-11-13 08:38:32,063 INFO sqlalchemy.engine.Engine [no key 0.00039s] ()
    2023-11-13 08:38:32,064 INFO sqlalchemy.engine.Engine COMMIT


#### Insert test data

We insert the test data using the `TableQuery` interface. Because this document is about select queries, feel free to look over this for now. I show the contents of the table as a dataframe below. The interface for doing this will be covered later in this document.


```python
import random
random.seed(0)

new_records: typing.List[Record] = list()
for i in range(10):
    age = int(random.random()*100) # number in [0,1]
    is_old = age > 50
    new_records.append(Record(name='user_'+str(i), age=age, is_old=is_old))

# insert new records
with rtab.query() as q:
    print(q.insert_multi(new_records))

# dataframe select (for example purposes - .df() will be covered later)
with core.query() as q:
    r = q.select(rtab.all_cols()).df()
r
```

    2023-11-13 08:38:32,104 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,104 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (age, is_old, name) VALUES (?, ?, ?)
    2023-11-13 08:38:32,105 INFO sqlalchemy.engine.Engine [generated in 0.00140s] [(84, True, 'user_0'), (75, True, 'user_1'), (42, False, 'user_2'), (25, False, 'user_3'), (51, True, 'user_4'), (40, False, 'user_5'), (78, True, 'user_6'), (30, False, 'user_7'), (47, False, 'user_8'), (58, True, 'user_9')]
    <sqlalchemy.engine.cursor.CursorResult object at 0x7feef3d133f0>
    2023-11-13 08:38:32,106 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-13 08:38:32,109 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,109 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 08:38:32,109 INFO sqlalchemy.engine.Engine [generated in 0.00102s] ()
    2023-11-13 08:38:32,112 INFO sqlalchemy.engine.Engine COMMIT





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>42</td>
      <td>0</td>
      <td>user_2</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>25</td>
      <td>0</td>
      <td>user_3</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>51</td>
      <td>1</td>
      <td>user_4</td>
    </tr>
    <tr>
      <th>5</th>
      <td>6</td>
      <td>40</td>
      <td>0</td>
      <td>user_5</td>
    </tr>
    <tr>
      <th>6</th>
      <td>7</td>
      <td>78</td>
      <td>1</td>
      <td>user_6</td>
    </tr>
    <tr>
      <th>7</th>
      <td>8</td>
      <td>30</td>
      <td>0</td>
      <td>user_7</td>
    </tr>
    <tr>
      <th>8</th>
      <td>9</td>
      <td>47</td>
      <td>0</td>
      <td>user_8</td>
    </tr>
    <tr>
      <th>9</th>
      <td>10</td>
      <td>58</td>
      <td>1</td>
      <td>user_9</td>
    </tr>
  </tbody>
</table>
</div>



## Two Interfaces: `ConnectQuery` and `TableQuery`

There are two interfaces for performing queries: `ConnectQuery` and `TableQuery`. 

+ **`ConnectQuery`** table-agnostic interface for querying any table in any result format.

+ **`TableQuery`** table-specific interface for querying a specific table. Insert and select from container objects used to define the schema.



```python
# ConnectQuery - table agnostic
with core.query() as q:
    print(type(q))

# TableQuery - queries are relative to specific 
# table, results appear as container objects
with rtab.query() as q:
    print(type(q))
```

    <class 'doctable.query.connectquery.ConnectQuery'>
    <class 'doctable.query.tablequery.TableQuery'>


## `ConnectQuery` Basics

First I will discuss the `ConnectQuery` interface, which is created via the `ConnectCore.query()` method. This object maintains a database connection, and, when used as a context manager, will commit all changes upon exit. It is fine to use the `ConnectQuery` object without a context manager for queries that do not require commits.

This example is the most basic select query we can execute. Note that `ConnectQuery` methods are table-agnostic, so we must specify columns to be selected - in this case, we provide `rtab.all_cols()` to specify that we want to query all columns from the `Record` table. It returns a `sqlalchemy.CursorResult` object that we will discuss later.


```python
core.query().select(rtab.all_cols())
```

    2023-11-13 08:38:32,204 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,205 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 08:38:32,205 INFO sqlalchemy.engine.Engine [cached since 0.09654s ago] ()





    <sqlalchemy.engine.cursor.CursorResult at 0x7feef3d88130>



### Selecting Specific Columns

In many cases, you would not want to select all columns from a given table - for this reason, there are several methods you can use to specify the desired columns. In addition to `.all_cols()` in the above snippet, you may use any of these methods.

| Method | Description |
| --- | --- |
| `.all_cols()` | specify that we want all columns |
| `.cols('col1', 'col2')` | specify set of columns |
| `table['col1']` | specify single column |
| `table[['col1', 'col2']]` | specify multiple columns |
| `table['col1':'col3']` | specify sequential range of columns |


```python
# select all columns
rtab.all_cols()
```




    [Column('id', Integer(), table=<Record>, primary_key=True),
     Column('age', Integer(), table=<Record>),
     Column('is_old', Integer(), table=<Record>),
     Column('name', String(), table=<Record>, nullable=False)]




```python
# .cols method
rtab.cols('id', 'name')
```




    [Column('id', Integer(), table=<Record>, primary_key=True),
     Column('name', String(), table=<Record>, nullable=False)]




```python
# single-column subscript
rtab['age']
```




    Column('age', Integer(), table=<Record>)




```python
# list of columns
rtab[['id','is_old']]
```




    [Column('id', Integer(), table=<Record>, primary_key=True),
     Column('is_old', Integer(), table=<Record>)]




```python
# slice select
rtab['id':'is_old']
```




    [Column('id', Integer(), table=<Record>, primary_key=True),
     Column('age', Integer(), table=<Record>),
     Column('is_old', Integer(), table=<Record>)]



Note that the `.select()` method requires a list of columns, so we can combine these methods by combining the lists they return. Obviously, the order matters for the returned values.


```python
rtab.cols('id','is_old') + [rtab['name']]
```




    [Column('id', Integer(), table=<Record>, primary_key=True),
     Column('is_old', Integer(), table=<Record>),
     Column('name', String(), table=<Record>, nullable=False)]



The `.select()` method always accepts a list of columns, so be sure to wrap single-column selections in a list.


```python
core.query().select([rtab['name']])
```

    2023-11-13 08:38:32,540 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,541 INFO sqlalchemy.engine.Engine SELECT "Record".name 
    FROM "Record"
    2023-11-13 08:38:32,542 INFO sqlalchemy.engine.Engine [generated in 0.00130s] ()





    <sqlalchemy.engine.cursor.CursorResult at 0x7feef3d12f90>




```python
core.query().select(rtab.cols('id','is_old') + [rtab['name']])
```

    2023-11-13 08:38:32,589 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,590 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 08:38:32,590 INFO sqlalchemy.engine.Engine [generated in 0.00142s] ()





    <sqlalchemy.engine.cursor.CursorResult at 0x7feef3d89010>



### Working with Query Results

Now we turn to working with the results objects. So far I have demonstrated values for returning `sqlalchemy.CursorResult` objects, but additional methods are required to return the results in a usable format. The following methods are available for various purposes:

| Method | Description |
| --- | --- |
| `result.all()` | return all results in query
| `result.df()` | return multiple results as a dataframe
| `result.first()` | return first result in query
| `result.one()` | return exactly one result in query. NOTE: raises exception if not exactly one result.
| `result.scalar_one()` | return single result, end query. NOTE: raises exception if not exactly one result.
| `result.scalars().all()` | return single column of results


```python
with core.query() as q:
    r = q.select(rtab.all_cols(), limit=3)
r.all()
```

    2023-11-13 08:38:32,637 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,638 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:32,639 INFO sqlalchemy.engine.Engine [generated in 0.00185s] (3, 0)
    2023-11-13 08:38:32,640 INFO sqlalchemy.engine.Engine COMMIT





    [(1, 84, 1, 'user_0'), (2, 75, 1, 'user_1'), (3, 42, 0, 'user_2')]




```python
core.query().select(rtab.all_cols(), limit=3).df()
```

    2023-11-13 08:38:32,689 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,690 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:32,690 INFO sqlalchemy.engine.Engine [cached since 0.05336s ago] (3, 0)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>42</td>
      <td>0</td>
      <td>user_2</td>
    </tr>
  </tbody>
</table>
</div>




```python
# raises exception without limit=1
core.query().select(rtab.all_cols()).first()
```

    2023-11-13 08:38:32,740 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,741 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 08:38:32,742 INFO sqlalchemy.engine.Engine [cached since 0.6331s ago] ()





    (1, 84, 1, 'user_0')




```python
# raises exception if more than one result is returned 
# (here I forced this with limit=1)
core.query().select(rtab.all_cols(), limit=1).one()
```

    2023-11-13 08:38:32,788 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,789 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:32,790 INFO sqlalchemy.engine.Engine [cached since 0.1527s ago] (1, 0)





    (1, 84, 1, 'user_0')




```python
# this returns the first column from the first row, then closes the cursor
core.query().select(rtab.all_cols(), limit=1).scalar_one()
```

    2023-11-13 08:38:32,837 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,838 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:32,838 INFO sqlalchemy.engine.Engine [cached since 0.2012s ago] (1, 0)





    1




```python
# it makes more sense to query a single column
core.query().select(rtab.cols('is_old'), limit=1).scalar_one()
```

    2023-11-13 08:38:32,889 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,890 INFO sqlalchemy.engine.Engine SELECT "Record".is_old 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:32,890 INFO sqlalchemy.engine.Engine [generated in 0.00136s] (1, 0)





    1




```python
# and when when you need a single column, use .scalars() instead of .all()
core.query().select(rtab.cols('is_old')).scalars().all()
```

    2023-11-13 08:38:32,940 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,941 INFO sqlalchemy.engine.Engine SELECT "Record".is_old 
    FROM "Record"
    2023-11-13 08:38:32,941 INFO sqlalchemy.engine.Engine [generated in 0.00138s] ()





    [1, 1, 0, 0, 1, 0, 1, 0, 0, 1]



### Conditional Select Statements

| operator | description |
| --- | --- |
| `&`, `doctable.exp.and_()` | and |
| `\|`, `doctable.exp.or_()` | or |
| `==` | equals |
| `!=`, `doctable.exp.not_()` | not equals |
| `>` | greater than |
| `>=` | greater than or equal to |
| `<` | less than |
| `<=` | less than or equal to |
| `in_()` | in list |
| `contains()` | check if item is substring |
| `like()` | like string |
| `ilike()` | case-insensitive like string |
| `between()`, `doctable.exp.between()` | between two values |
| `is_()` | is value |
| `isnot()` | is not value |
| `startswith()` | starts with string |


```python
core.query().select(rtab.all_cols(), where=rtab['id']==2).df()
```

    2023-11-13 08:38:32,989 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:32,990 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".id = ?
    2023-11-13 08:38:32,990 INFO sqlalchemy.engine.Engine [generated in 0.00131s] (2,)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
  </tbody>
</table>
</div>




```python
core.query().select(rtab.all_cols(), where=rtab['id']<rtab['id']).df()
```

    2023-11-13 08:38:33,037 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,038 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".id < "Record".id
    2023-11-13 08:38:33,038 INFO sqlalchemy.engine.Engine [generated in 0.00128s] ()





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>




```python
core.query().select(rtab.all_cols(), where=(rtab['id']%2)==0).df()
```

    2023-11-13 08:38:33,089 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,090 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".id % ? = ?
    2023-11-13 08:38:33,091 INFO sqlalchemy.engine.Engine [generated in 0.00138s] (2, 0)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4</td>
      <td>25</td>
      <td>0</td>
      <td>user_3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>6</td>
      <td>40</td>
      <td>0</td>
      <td>user_5</td>
    </tr>
    <tr>
      <th>3</th>
      <td>8</td>
      <td>30</td>
      <td>0</td>
      <td>user_7</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10</td>
      <td>58</td>
      <td>1</td>
      <td>user_9</td>
    </tr>
  </tbody>
</table>
</div>




```python
condition = (rtab['id']>=2) & (rtab['id']<=4) & (rtab['name']!='user_2')
core.query().select(rtab.all_cols(), where=condition).df()
```

    2023-11-13 08:38:33,142 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,143 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".id >= ? AND "Record".id <= ? AND "Record".name != ?
    2023-11-13 08:38:33,143 INFO sqlalchemy.engine.Engine [generated in 0.00147s] (2, 4, 'user_2')





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4</td>
      <td>25</td>
      <td>0</td>
      <td>user_3</td>
    </tr>
  </tbody>
</table>
</div>




```python
condition = rtab['name'].in_(('user_2','user_3'))
core.query().select(rtab.all_cols(), where=condition).df()
```

    2023-11-13 08:38:33,194 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,195 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".name IN (?, ?)
    2023-11-13 08:38:33,195 INFO sqlalchemy.engine.Engine [generated in 0.00146s] ('user_2', 'user_3')





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3</td>
      <td>42</td>
      <td>0</td>
      <td>user_2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4</td>
      <td>25</td>
      <td>0</td>
      <td>user_3</td>
    </tr>
  </tbody>
</table>
</div>




```python
core.query().select(rtab.all_cols(), where=rtab['id'].between(2,4)).df()
```

    2023-11-13 08:38:33,246 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,247 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".id BETWEEN ? AND ?
    2023-11-13 08:38:33,247 INFO sqlalchemy.engine.Engine [generated in 0.00134s] (2, 4)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3</td>
      <td>42</td>
      <td>0</td>
      <td>user_2</td>
    </tr>
    <tr>
      <th>2</th>
      <td>4</td>
      <td>25</td>
      <td>0</td>
      <td>user_3</td>
    </tr>
  </tbody>
</table>
</div>




```python
condition = ~(rtab['name'].in_(('user_2','user_3'))) & (rtab['id'] < 4)
core.query().select(rtab.all_cols(), where=condition).df()
```

    2023-11-13 08:38:33,298 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,299 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE ("Record".name NOT IN (?, ?)) AND "Record".id < ?
    2023-11-13 08:38:33,300 INFO sqlalchemy.engine.Engine [generated in 0.00171s] ('user_2', 'user_3', 4)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
  </tbody>
</table>
</div>




```python
condition = doctable.exp.or_(doctable.exp.not_(rtab['id']==4)) & (rtab['id'] <= 2)
core.query().select(rtab.all_cols(), where=condition).df()
```

    2023-11-13 08:38:33,350 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,351 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".id != ? AND "Record".id <= ?
    2023-11-13 08:38:33,352 INFO sqlalchemy.engine.Engine [generated in 0.00181s] (4, 2)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
  </tbody>
</table>
</div>




```python
with core.query() as q:
    ages = q.select([rtab['age']]).scalars().all()
    mean_age = sum(ages)/len(ages)
    result = q.select(rtab.all_cols(), where=rtab['age']>mean_age)
result.df()
```

    2023-11-13 08:38:33,402 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,404 INFO sqlalchemy.engine.Engine SELECT "Record".age 
    FROM "Record"
    2023-11-13 08:38:33,404 INFO sqlalchemy.engine.Engine [generated in 0.00155s] ()
    2023-11-13 08:38:33,406 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".age > ?
    2023-11-13 08:38:33,406 INFO sqlalchemy.engine.Engine [generated in 0.00045s] (53.0,)
    2023-11-13 08:38:33,407 INFO sqlalchemy.engine.Engine COMMIT





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>7</td>
      <td>78</td>
      <td>1</td>
      <td>user_6</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10</td>
      <td>58</td>
      <td>1</td>
      <td>user_9</td>
    </tr>
  </tbody>
</table>
</div>



### Column Operators

In addition to any of the methods used for conditional selects, there are several additional methods that can be used to transform columns in the select statement.

| Method | Description |
| --- | --- |
| `.label()` | rename column in result (particularly useful after transformations) |
| `.min()`, `doctable.f.min()` | max of column values |
| `.max()`, `doctable.f.max()` | max of column values |
| `.sum()`, `doctable.f.sum()` | sum of column |
| `.count()`, `doctable.f.count()` | count number of results. *NOTE*: must use `f.count()` when counting transformed columns. |
| `.distinct()`, `doctable.f.distinct()` | get distinct values |
| `/` | divide |
| `*` | multiply |
| `+` | add |
| `-` | subtract |
| `%` | modulo |
| `.concat()` | concatenate strings |


```python
columns = [
    (rtab['id'] % 2).label('mod_id'), 
    rtab['name'].label('myname')
]
core.query().select(columns, where=rtab['is_old']).df()
```

    2023-11-13 08:38:33,457 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,458 INFO sqlalchemy.engine.Engine SELECT "Record".id % ? AS mod_id, "Record".name AS myname 
    FROM "Record" 
    WHERE "Record".is_old
    2023-11-13 08:38:33,458 INFO sqlalchemy.engine.Engine [generated in 0.00153s] (2,)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mod_id</th>
      <th>myname</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>user_4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>user_6</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>user_9</td>
    </tr>
  </tbody>
</table>
</div>




```python
formula = rtab['age'].sum() / rtab['age'].count()
core.query().select([formula]).scalar_one()
```

    2023-11-13 08:38:33,510 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,511 INFO sqlalchemy.engine.Engine SELECT sum("Record".age) / (count("Record".age) + 0.0) AS anon_1 
    FROM "Record"
    2023-11-13 08:38:33,511 INFO sqlalchemy.engine.Engine [generated in 0.00153s] ()





    Decimal('53.0000000000')




```python
formula = rtab['age'].max() - rtab['age'].min()
core.query().select([formula]).scalar_one()
```

    2023-11-13 08:38:33,561 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,562 INFO sqlalchemy.engine.Engine SELECT max("Record".age) - min("Record".age) AS anon_1 
    FROM "Record"
    2023-11-13 08:38:33,563 INFO sqlalchemy.engine.Engine [generated in 0.00155s] ()





    59




```python
# average age of individuals over 30
formula = rtab['age'].sum() / rtab['age'].count()
condition = rtab['age'] > 30
core.query().select([formula], where=condition).scalar_one()
```

    2023-11-13 08:38:33,614 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,615 INFO sqlalchemy.engine.Engine SELECT sum("Record".age) / (count("Record".age) + 0.0) AS anon_1 
    FROM "Record" 
    WHERE "Record".age > ?
    2023-11-13 08:38:33,615 INFO sqlalchemy.engine.Engine [generated in 0.00140s] (30,)





    Decimal('59.3750000000')




```python
# descriptive stats on age of individuals over 30
columns = [
    (rtab['age'].sum() / rtab['age'].count()).label('mean'),
    rtab['age'].max().label('max'),
    rtab['age'].min().label('min'),
]
condition = rtab['age'] > 30
core.query().select(columns, where=condition).df()
```

    2023-11-13 08:38:33,666 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,667 INFO sqlalchemy.engine.Engine SELECT sum("Record".age) / (count("Record".age) + 0.0) AS mean, max("Record".age) AS max, min("Record".age) AS min 
    FROM "Record" 
    WHERE "Record".age > ?
    2023-11-13 08:38:33,667 INFO sqlalchemy.engine.Engine [generated in 0.00142s] (30,)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mean</th>
      <th>max</th>
      <th>min</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>59.3750000000</td>
      <td>84</td>
      <td>40</td>
    </tr>
  </tbody>
</table>
</div>




```python
# all distinct values
formula = rtab['is_old'].distinct()
core.query().select([formula]).df()
```

    2023-11-13 08:38:33,717 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,718 INFO sqlalchemy.engine.Engine SELECT distinct("Record".is_old) AS distinct_1 
    FROM "Record"
    2023-11-13 08:38:33,718 INFO sqlalchemy.engine.Engine [generated in 0.00171s] ()





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>distinct_1</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
# count individuals over 30
core.query().select([doctable.f.count()], where=rtab['age']>30).scalar_one()
```

    2023-11-13 08:38:33,765 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,766 INFO sqlalchemy.engine.Engine SELECT count(*) AS count_1 
    FROM "Record" 
    WHERE "Record".age > ?
    2023-11-13 08:38:33,767 INFO sqlalchemy.engine.Engine [generated in 0.00157s] (30,)





    8




```python
# similar to previous
core.query().select([rtab['id'].count()], where=rtab['age']>30).scalar_one()
```

    2023-11-13 08:38:33,817 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,818 INFO sqlalchemy.engine.Engine SELECT count("Record".id) AS count_1 
    FROM "Record" 
    WHERE "Record".age > ?
    2023-11-13 08:38:33,818 INFO sqlalchemy.engine.Engine [generated in 0.00127s] (30,)





    8



### Additional Parameters: Order By, Group By, Limit, Offset

More complicated queries involving ordering, grouping, limiting, and specifying offset can be specified using parameters to the `.select()` method.

| Parameter | Description |
| --- | --- |
| `limit` | limit number of results |
| `order_by` | list of columns to order by |
| `group_by` | list of columns to group by |
| `offset` | offset results by specified number |

#### Order By and Limits


```python
# get the five youngest individuals in order
core.query().select(rtab.all_cols(), order_by=rtab['age'], limit=5).df()
```

    2023-11-13 08:38:33,865 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,865 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" ORDER BY "Record".age
     LIMIT ? OFFSET ?
    2023-11-13 08:38:33,866 INFO sqlalchemy.engine.Engine [generated in 0.00127s] (5, 0)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>4</td>
      <td>25</td>
      <td>0</td>
      <td>user_3</td>
    </tr>
    <tr>
      <th>1</th>
      <td>8</td>
      <td>30</td>
      <td>0</td>
      <td>user_7</td>
    </tr>
    <tr>
      <th>2</th>
      <td>6</td>
      <td>40</td>
      <td>0</td>
      <td>user_5</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>42</td>
      <td>0</td>
      <td>user_2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>9</td>
      <td>47</td>
      <td>0</td>
      <td>user_8</td>
    </tr>
  </tbody>
</table>
</div>




```python
# get the five oldest now
core.query().select(rtab.all_cols(), order_by=rtab['age'].desc(), limit=5).df()
```

    2023-11-13 08:38:33,913 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,914 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" ORDER BY "Record".age DESC
     LIMIT ? OFFSET ?
    2023-11-13 08:38:33,915 INFO sqlalchemy.engine.Engine [generated in 0.00165s] (5, 0)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>7</td>
      <td>78</td>
      <td>1</td>
      <td>user_6</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>3</th>
      <td>10</td>
      <td>58</td>
      <td>1</td>
      <td>user_9</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>51</td>
      <td>1</td>
      <td>user_4</td>
    </tr>
  </tbody>
</table>
</div>




```python
# order by is_old, but preserve order of id otherwise
order = [
    rtab['is_old'].desc(),
    rtab['id'].asc(),
]
core.query().select(rtab.all_cols(), order_by=order, limit=5).df()
```

    2023-11-13 08:38:33,965 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:33,966 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" ORDER BY "Record".is_old DESC, "Record".id ASC
     LIMIT ? OFFSET ?
    2023-11-13 08:38:33,966 INFO sqlalchemy.engine.Engine [generated in 0.00135s] (5, 0)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>84</td>
      <td>1</td>
      <td>user_0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>75</td>
      <td>1</td>
      <td>user_1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>5</td>
      <td>51</td>
      <td>1</td>
      <td>user_4</td>
    </tr>
    <tr>
      <th>3</th>
      <td>7</td>
      <td>78</td>
      <td>1</td>
      <td>user_6</td>
    </tr>
    <tr>
      <th>4</th>
      <td>10</td>
      <td>58</td>
      <td>1</td>
      <td>user_9</td>
    </tr>
  </tbody>
</table>
</div>



#### Grouping and Column Operators


```python
# summary stats by is_old
cols = [
    #rtab['is_old'].count().label('count'),
    doctable.f.count().label('count'),
    rtab['age'].min().label('min'),
    rtab['age'].max().label('max'),
    (rtab['age'].sum()/rtab['age'].count()).label('mean'),
]
core.query().select(cols, group_by=rtab['is_old']).df()
```

    2023-11-13 08:38:34,018 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,019 INFO sqlalchemy.engine.Engine SELECT count(*) AS count, min("Record".age) AS min, max("Record".age) AS max, sum("Record".age) / (count("Record".age) + 0.0) AS mean 
    FROM "Record" GROUP BY "Record".is_old
    2023-11-13 08:38:34,019 INFO sqlalchemy.engine.Engine [generated in 0.00141s] ()





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>count</th>
      <th>min</th>
      <th>max</th>
      <th>mean</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>5</td>
      <td>25</td>
      <td>47</td>
      <td>36.8000000000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>5</td>
      <td>51</td>
      <td>84</td>
      <td>69.2000000000</td>
    </tr>
  </tbody>
</table>
</div>




```python
# summarize age by decade
decade_expression = doctable.f.round(rtab['age'] / 10)
cols = [
    decade_expression.label('decade'),
    rtab['age'].count().label('count'),
    rtab['age'].min().label('min'),
    rtab['age'].max().label('max'),
    (rtab['age'].sum()/rtab['age'].count()).label('mean'),
]
core.query().select(cols, group_by=decade_expression).df()
```

    2023-11-13 08:38:34,070 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,071 INFO sqlalchemy.engine.Engine SELECT round("Record".age / (? + 0.0)) AS decade, count("Record".age) AS count, min("Record".age) AS min, max("Record".age) AS max, sum("Record".age) / (count("Record".age) + 0.0) AS mean 
    FROM "Record" GROUP BY round("Record".age / (? + 0.0))
    2023-11-13 08:38:34,072 INFO sqlalchemy.engine.Engine [generated in 0.00134s] (10, 10)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>decade</th>
      <th>count</th>
      <th>min</th>
      <th>max</th>
      <th>mean</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3.0</td>
      <td>2</td>
      <td>25</td>
      <td>30</td>
      <td>27.5000000000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4.0</td>
      <td>2</td>
      <td>40</td>
      <td>42</td>
      <td>41.0000000000</td>
    </tr>
    <tr>
      <th>2</th>
      <td>5.0</td>
      <td>2</td>
      <td>47</td>
      <td>51</td>
      <td>49.0000000000</td>
    </tr>
    <tr>
      <th>3</th>
      <td>6.0</td>
      <td>1</td>
      <td>58</td>
      <td>58</td>
      <td>58.0000000000</td>
    </tr>
    <tr>
      <th>4</th>
      <td>8.0</td>
      <td>3</td>
      <td>75</td>
      <td>84</td>
      <td>79.0000000000</td>
    </tr>
  </tbody>
</table>
</div>



#### Offset and Selecting Chunks

The `offset` parameter is used to pagify results into multiple queries - something that is particularly useful if the result set is too larget to fit into memory.


```python
# get the three oldest individuals, offset by three
core.query().select(rtab.all_cols(), order_by=rtab['age'].desc(), limit=3, offset=3).df()
```

    2023-11-13 08:38:34,121 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,121 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" ORDER BY "Record".age DESC
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,122 INFO sqlalchemy.engine.Engine [generated in 0.00137s] (3, 3)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>age</th>
      <th>is_old</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10</td>
      <td>58</td>
      <td>1</td>
      <td>user_9</td>
    </tr>
    <tr>
      <th>1</th>
      <td>5</td>
      <td>51</td>
      <td>1</td>
      <td>user_4</td>
    </tr>
    <tr>
      <th>2</th>
      <td>9</td>
      <td>47</td>
      <td>0</td>
      <td>user_8</td>
    </tr>
  </tbody>
</table>
</div>




```python
for chunk in core.query().select_chunks(rtab.all_cols(), chunksize=3):
    print(chunk)
```

    2023-11-13 08:38:34,169 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,169 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,170 INFO sqlalchemy.engine.Engine [generated in 0.00117s] (3, 0)
    [(1, 84, 1, 'user_0'), (2, 75, 1, 'user_1'), (3, 42, 0, 'user_2')]
    2023-11-13 08:38:34,171 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,171 INFO sqlalchemy.engine.Engine [cached since 0.002855s ago] (3, 3)
    [(4, 25, 0, 'user_3'), (5, 51, 1, 'user_4'), (6, 40, 0, 'user_5')]
    2023-11-13 08:38:34,172 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,173 INFO sqlalchemy.engine.Engine [cached since 0.004328s ago] (3, 6)
    [(7, 78, 1, 'user_6'), (8, 30, 0, 'user_7'), (9, 47, 0, 'user_8')]
    2023-11-13 08:38:34,175 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,175 INFO sqlalchemy.engine.Engine [cached since 0.006853s ago] (3, 9)
    [(10, 58, 1, 'user_9')]


## `TableQuery` Basics

The `TableQuery` interface is used to make table-specific queries, and, in exchange for this restriction, allows you to insert and select container objects directly. Queries on tables look much like their table-agnostic counterparts, with a few exceptions. Every query still begins with the `.query()` method, which returns a `TableQuery` object with methods for inserting and selecting container objects.

1. List of selected columns is optional - if you do not specify, the query will default to all columns in the table. Otherwise, you should provide a subset of the columns, where all attributes that were not received will refer to `doctable.MISSING`, which you may check for downstream.

2. Results of a select query are returned as a list of container objects. This means that we have called the `.all()` method on the `sqlalchemy.CursorResult` object.

3. All returned results must match the attributes of the container object. Most often you will want to select raw database rows, but transformations via `group_by` and other operators are also possible as long as the result set attributes match the container attributes - that is, they can be expanded to the container constructor.

4. Behavior of `where`, `order_by`, `limit`, are `offset` all operate as-expected.

Below you can see a few examples demonstrating this behavior.


```python
rtab.query().select(where=rtab['age']>50)
```

    2023-11-13 08:38:34,217 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,218 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record" 
    WHERE "Record".age > ?
    2023-11-13 08:38:34,219 INFO sqlalchemy.engine.Engine [generated in 0.00128s] (50,)





    [Record(name='user_0', age=84, is_old=1, id=1),
     Record(name='user_1', age=75, is_old=1, id=2),
     Record(name='user_4', age=51, is_old=1, id=5),
     Record(name='user_6', age=78, is_old=1, id=7),
     Record(name='user_9', age=58, is_old=1, id=10)]




```python
result = rtab.query().select(rtab.cols('id', 'age'), where=rtab['is_old'])
f'{result[0].name is doctable.MISSING=}', result
```

    2023-11-13 08:38:34,268 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,269 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age 
    FROM "Record" 
    WHERE "Record".is_old
    2023-11-13 08:38:34,270 INFO sqlalchemy.engine.Engine [generated in 0.00134s] ()





    ('result[0].name is doctable.MISSING=True',
     [Record(name=MISSING, age=84, is_old=MISSING, id=1),
      Record(name=MISSING, age=75, is_old=MISSING, id=2),
      Record(name=MISSING, age=51, is_old=MISSING, id=5),
      Record(name=MISSING, age=78, is_old=MISSING, id=7),
      Record(name=MISSING, age=58, is_old=MISSING, id=10)])




```python
# this is valid, although perhaps not recommended
cols = [
    (rtab['age'].sum()/rtab['age'].count()).label('age'),
]
rtab.query().select(cols=cols)
```

    2023-11-13 08:38:34,317 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,318 INFO sqlalchemy.engine.Engine SELECT sum("Record".age) / (count("Record".age) + 0.0) AS age 
    FROM "Record"
    2023-11-13 08:38:34,318 INFO sqlalchemy.engine.Engine [generated in 0.00123s] ()





    [Record(name=MISSING, age=Decimal('53.0000000000'), is_old=MISSING, id=MISSING)]



`.select_chunks()` also more or less works as-expected, with the chunks being converted to container objects.


```python
for chunk in rtab.query().select_chunks(chunksize=3):
    print(chunk)
```

    2023-11-13 08:38:34,364 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 08:38:34,365 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,365 INFO sqlalchemy.engine.Engine [cached since 0.1964s ago] (3, 0)
    [Record(name='user_0', age=84, is_old=1, id=1), Record(name='user_1', age=75, is_old=1, id=2), Record(name='user_2', age=42, is_old=0, id=3)]
    2023-11-13 08:38:34,366 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,367 INFO sqlalchemy.engine.Engine [cached since 0.198s ago] (3, 3)
    [Record(name='user_3', age=25, is_old=0, id=4), Record(name='user_4', age=51, is_old=1, id=5), Record(name='user_5', age=40, is_old=0, id=6)]
    2023-11-13 08:38:34,368 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,368 INFO sqlalchemy.engine.Engine [cached since 0.1994s ago] (3, 6)
    [Record(name='user_6', age=78, is_old=1, id=7), Record(name='user_7', age=30, is_old=0, id=8), Record(name='user_8', age=47, is_old=0, id=9)]
    2023-11-13 08:38:34,369 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
     LIMIT ? OFFSET ?
    2023-11-13 08:38:34,369 INFO sqlalchemy.engine.Engine [cached since 0.2007s ago] (3, 9)
    [Record(name='user_9', age=58, is_old=1, id=10)]

