# Insert and Delete Queries

In this document I will describe the interface for performing insert and delete queries with doctable.


```

import pandas as pd
import numpy as np
import typing

import sys
sys.path.append('..')
import doctable
```

#### Define a demonstration schema

The very first step is to define a table schema that will be appropriate for our examples. This table includes the typical `id` column (the first column, specified by `order=0`), as well as string, integer, and boolean attributes. The object used to specify the schema is called a _container_, and I will use that terminology as we go.


```
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

    2023-11-13 14:46:03,418 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,418 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("Record")
    2023-11-13 14:46:03,419 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-13 14:46:03,420 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("Record")
    2023-11-13 14:46:03,421 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-13 14:46:03,422 INFO sqlalchemy.engine.Engine 
    CREATE TABLE "Record" (
    	id INTEGER, 
    	age INTEGER, 
    	is_old INTEGER, 
    	name VARCHAR NOT NULL, 
    	PRIMARY KEY (id), 
    	UNIQUE (name)
    )
    
    
    2023-11-13 14:46:03,423 INFO sqlalchemy.engine.Engine [no key 0.00050s] ()
    2023-11-13 14:46:03,424 INFO sqlalchemy.engine.Engine COMMIT


## Two Interfaces: `ConnectQuery` and `TableQuery`

First, a little about the `doctable` query interface. There are two interfaces for performing queries: `ConnectQuery` and `TableQuery`. 

+ **`ConnectQuery`** table-agnostic interface for querying any table in any result format. Create this object using the `ConnectCore.query()` method.

+ **`TableQuery`** table-specific interface for querying a specific table. Insert and select from container objects used to define the schema. Create this object using the `DBTable.query()` method.

### Inserts via `ConnectQuery`

First I will discuss the `ConnectQuery` interface, which is created via the `ConnectCore.query()` method. This object maintains a database connection, and, when used as a context manager, will commit all changes upon exit. It is fine to use the `ConnectQuery` object without a context manager for queries that do not require commits.

There are two primary methods for insertions via the `ConnectQuery` interface, which you can see in this table. Both accept a single `DBTable` object, followed by one or multiple dictionaries of data to insert, depending on the method.

| Method | Description |
| --- | --- |
| `insert_single()` | Insert a single row into a table. |
| `insert_multi()` | Insert multiple rows into a table. |


```
with core.query() as q:
    q.insert_single(rtab, {
        'name': 'test_A',
        'age': 10,
        'is_old': False,
    })
    
    q.insert_multi(rtab, data = [
        {
            'name': 'test_B',
            'age': 10,
            'is_old': False,
        },
        {
            'name': 'test_C',
            'age': 10,
            'is_old': False,
        }
    ])
    
q.select(rtab.all_cols()).df()
```

    2023-11-13 14:46:03,478 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,480 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (age, is_old, name) VALUES (?, ?, ?)
    2023-11-13 14:46:03,482 INFO sqlalchemy.engine.Engine [generated in 0.00420s] (10, False, 'test_A')
    2023-11-13 14:46:03,487 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (age, is_old, name) VALUES (?, ?, ?)
    2023-11-13 14:46:03,489 INFO sqlalchemy.engine.Engine [generated in 0.00216s] [(10, False, 'test_B'), (10, False, 'test_C')]
    2023-11-13 14:46:03,491 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-13 14:46:03,494 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,495 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 14:46:03,497 INFO sqlalchemy.engine.Engine [generated in 0.00319s] ()





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
      <td>10</td>
      <td>0</td>
      <td>test_A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>10</td>
      <td>0</td>
      <td>test_B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>10</td>
      <td>0</td>
      <td>test_C</td>
    </tr>
  </tbody>
</table>
</div>



#### Omit Attributes

If some values are not provided, the database will decide which values they take. In this case, the database populates the ID column according to the schema (it acts as the primary key in this case).


```
core.query().insert_single(rtab, {
    'name': 'test_D',
})
core.query().select(rtab.all_cols()).df()
```

    2023-11-13 14:46:03,544 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,546 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (name) VALUES (?)
    2023-11-13 14:46:03,548 INFO sqlalchemy.engine.Engine [generated in 0.00389s] ('test_D',)
    2023-11-13 14:46:03,551 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,552 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 14:46:03,554 INFO sqlalchemy.engine.Engine [cached since 0.06015s ago] ()





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
      <td>10.0</td>
      <td>0.0</td>
      <td>test_A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>10.0</td>
      <td>0.0</td>
      <td>test_B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>10.0</td>
      <td>0.0</td>
      <td>test_C</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>test_D</td>
    </tr>
  </tbody>
</table>
</div>



Note that in our schema we set `nullable=False` for the name column, so this must be provided in an insert otherwise there will be an error. This typically results in an `sqlalchemy.exc.IntegrityError`, which you may catch if needed.


```
import sqlalchemy.exc

try:
    core.query().insert_single(rtab, {
        'is_old': True,
    })
except sqlalchemy.exc.IntegrityError as e:
    print(type(e), e)
```

    2023-11-13 14:46:03,605 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,607 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (is_old) VALUES (?)
    2023-11-13 14:46:03,609 INFO sqlalchemy.engine.Engine [generated in 0.00380s] (True,)
    <class 'sqlalchemy.exc.IntegrityError'> (sqlite3.IntegrityError) NOT NULL constraint failed: Record.name
    [SQL: INSERT OR FAIL INTO "Record" (is_old) VALUES (?)]
    [parameters: (True,)]
    (Background on this error at: https://sqlalche.me/e/20/gkpj)


#### `ifnotunique` Parameter

The `ifnotunique` paramter controls the behavior when a unique constraint is violated. 

The default value is `FAIL`, which will raise an error when a unique constraint is violated - it will raise an `sqlalchemy.exc.IntegrityError` exception in this case. The other options are `IGNORE`, meaning inserted rows that violate the constraints should be ignored, and `REPLACE`, which will replace the existing row with the new row.

In the `Record` table we have created, there is a unique constraint on `name`. We will receive an integrity error if we try to insert a duplicate there when using the default `ifnotunique='ERROR'`.


```
try:
    core.query().insert_single(rtab, {
        'name': 'test_A',
    })
except sqlalchemy.exc.IntegrityError as e:
    print(type(e), e)
```

    2023-11-13 14:46:03,665 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,668 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (name) VALUES (?)
    2023-11-13 14:46:03,669 INFO sqlalchemy.engine.Engine [cached since 0.1247s ago] ('test_A',)
    <class 'sqlalchemy.exc.IntegrityError'> (sqlite3.IntegrityError) UNIQUE constraint failed: Record.name
    [SQL: INSERT OR FAIL INTO "Record" (name) VALUES (?)]
    [parameters: ('test_A',)]
    (Background on this error at: https://sqlalche.me/e/20/gkpj)


When using `ifnotunique='REPLACE'`, the insert will replace the existing row with the new row. This is useful when you want to update a row if it already exists, but insert it if it does not.


```
core.query().insert_single(rtab, {
    'name': 'test_A',
}, ifnotunique='REPLACE')
core.query().select(rtab.all_cols()).df()
```

    2023-11-13 14:46:03,728 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,731 INFO sqlalchemy.engine.Engine INSERT OR REPLACE INTO "Record" (name) VALUES (?)
    2023-11-13 14:46:03,733 INFO sqlalchemy.engine.Engine [generated in 0.00453s] ('test_A',)
    2023-11-13 14:46:03,738 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,739 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 14:46:03,741 INFO sqlalchemy.engine.Engine [cached since 0.2469s ago] ()





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
      <td>10.0</td>
      <td>0.0</td>
      <td>test_B</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3</td>
      <td>10.0</td>
      <td>0.0</td>
      <td>test_C</td>
    </tr>
    <tr>
      <th>2</th>
      <td>4</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>test_D</td>
    </tr>
    <tr>
      <th>3</th>
      <td>5</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>test_A</td>
    </tr>
  </tbody>
</table>
</div>



## Inserts via `TableQuery`

The `TableQuery` interface is created via the `DBTable.query()` method. This object is table-specific, and is used to insert and select from a single table. As such, inserts ONLY accept the `Record` container objects used to define the schema. Following the `ConnectQuery` interface, there are two methods for inserting data into a table: `.insert_single()` and `.insert_multi()`.


```
rtab.query().insert_single(Record(name='test_E', is_old=False, age=10))
rtab.query().select(rtab.all_cols())
```

    2023-11-13 14:46:03,806 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,809 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (age, is_old, name) VALUES (?, ?, ?)
    2023-11-13 14:46:03,811 INFO sqlalchemy.engine.Engine [cached since 0.3334s ago] (10, False, 'test_E')
    2023-11-13 14:46:03,814 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,815 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 14:46:03,816 INFO sqlalchemy.engine.Engine [cached since 0.3218s ago] ()





    [Record(name='test_B', age=10, is_old=0, id=2),
     Record(name='test_C', age=10, is_old=0, id=3),
     Record(name='test_D', age=None, is_old=None, id=4),
     Record(name='test_A', age=None, is_old=None, id=5),
     Record(name='test_E', age=10, is_old=0, id=6)]




```
rtab.query().insert_multi([
    Record(name='test_F', is_old=False, age=10),
    Record(name='test_G', is_old=True, age=80),
])
rtab.query().select(rtab.all_cols())
```

    2023-11-13 14:46:03,866 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,869 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (age, is_old, name) VALUES (?, ?, ?)
    2023-11-13 14:46:03,870 INFO sqlalchemy.engine.Engine [cached since 0.3834s ago] [(10, False, 'test_F'), (80, True, 'test_G')]
    2023-11-13 14:46:03,874 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,875 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 14:46:03,876 INFO sqlalchemy.engine.Engine [cached since 0.3818s ago] ()





    [Record(name='test_B', age=10, is_old=0, id=2),
     Record(name='test_C', age=10, is_old=0, id=3),
     Record(name='test_D', age=None, is_old=None, id=4),
     Record(name='test_A', age=None, is_old=None, id=5),
     Record(name='test_E', age=10, is_old=0, id=6),
     Record(name='test_F', age=10, is_old=0, id=7),
     Record(name='test_G', age=80, is_old=1, id=8)]



#### The `doctable.MISSING` Sentinel

Lets now take a closer look at the container object behavior. Notice that in the schema definition we gave default values of `doctable.Column`, which we used to specify additional attributes. This automatically sets the default value for the dataclass to be `doctable.MISSING`, which is special because it will be ignored when inserting - instead, it will let the database decide how to handle it. This is especially useful for columns like `id`, which are intended to be automatically generated by the database. We can see this when we omit attributes from the object.


```
test_record = Record(name='test_H')
test_record
```




    Record(name='test_H', age=MISSING, is_old=MISSING, id=MISSING)



Those values will be omitted in the insert, filled in by the db, and be returned upon selection.


```
rtab.query().insert_single(test_record)
rtab.query().select(rtab.all_cols())
```

    2023-11-13 14:46:03,982 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,985 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO "Record" (name) VALUES (?)
    2023-11-13 14:46:03,987 INFO sqlalchemy.engine.Engine [cached since 0.4426s ago] ('test_H',)
    2023-11-13 14:46:03,990 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:03,991 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".age, "Record".is_old, "Record".name 
    FROM "Record"
    2023-11-13 14:46:03,992 INFO sqlalchemy.engine.Engine [cached since 0.4979s ago] ()





    [Record(name='test_B', age=10, is_old=0, id=2),
     Record(name='test_C', age=10, is_old=0, id=3),
     Record(name='test_D', age=None, is_old=None, id=4),
     Record(name='test_A', age=None, is_old=None, id=5),
     Record(name='test_E', age=10, is_old=0, id=6),
     Record(name='test_F', age=10, is_old=0, id=7),
     Record(name='test_G', age=80, is_old=1, id=8),
     Record(name='test_H', age=None, is_old=None, id=9)]



If we select a subset of columns, the missing values will refer to `doctable.MISSING`, even though the attributes will continue to exist.


```
rtab.query().select(rtab.cols('id', 'name'))
```

    2023-11-13 14:46:04,041 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:04,044 INFO sqlalchemy.engine.Engine SELECT "Record".id, "Record".name 
    FROM "Record"
    2023-11-13 14:46:04,045 INFO sqlalchemy.engine.Engine [generated in 0.00350s] ()





    [Record(name='test_A', age=MISSING, is_old=MISSING, id=5),
     Record(name='test_B', age=MISSING, is_old=MISSING, id=2),
     Record(name='test_C', age=MISSING, is_old=MISSING, id=3),
     Record(name='test_D', age=MISSING, is_old=MISSING, id=4),
     Record(name='test_E', age=MISSING, is_old=MISSING, id=6),
     Record(name='test_F', age=MISSING, is_old=MISSING, id=7),
     Record(name='test_G', age=MISSING, is_old=MISSING, id=8),
     Record(name='test_H', age=MISSING, is_old=MISSING, id=9)]



Note that the `doctable.MISSING` will never be inserted into the databse because it will be ignored.

## Deletion Interface

Deleting rows is pretty straightforward when using either the `ConnectQuery` or `TableQuery` interfaces. In fact, it is the exact same for both. The only parameters are `where` and `wherestr` (where you can add additional conditionals as strings).


```
print(core.query().select([rtab['id'].count()]).scalar_one())
with rtab.query() as q:
    q.delete(where=rtab['name']=='test_A')
core.query().select([rtab['id'].count()]).scalar_one()
```

    2023-11-13 14:46:31,486 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:31,489 INFO sqlalchemy.engine.Engine SELECT count("Record".id) AS count_1 
    FROM "Record"
    2023-11-13 14:46:31,490 INFO sqlalchemy.engine.Engine [cached since 27.39s ago] ()
    7
    2023-11-13 14:46:31,493 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:31,495 INFO sqlalchemy.engine.Engine DELETE FROM "Record" WHERE "Record".name = ?
    2023-11-13 14:46:31,497 INFO sqlalchemy.engine.Engine [cached since 27.39s ago] ('test_A',)
    2023-11-13 14:46:31,498 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-13 14:46:31,500 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:46:31,500 INFO sqlalchemy.engine.Engine SELECT count("Record".id) AS count_1 
    FROM "Record"
    2023-11-13 14:46:31,501 INFO sqlalchemy.engine.Engine [cached since 27.4s ago] ()





    7



To delete all columns, pass the `all=True` flag. This prevents the user from accidentally deleting all rows.


```
with rtab.query() as q:
    q.delete(all=True)
core.query().select([rtab['id'].count()]).scalar_one()
```

    2023-11-13 14:48:08,718 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:48:08,720 INFO sqlalchemy.engine.Engine DELETE FROM "Record"
    2023-11-13 14:48:08,722 INFO sqlalchemy.engine.Engine [cached since 13.97s ago] ()
    2023-11-13 14:48:08,724 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-13 14:48:08,726 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-13 14:48:08,727 INFO sqlalchemy.engine.Engine SELECT count("Record".id) AS count_1 
    FROM "Record"
    2023-11-13 14:48:08,729 INFO sqlalchemy.engine.Engine [cached since 124.6s ago] ()





    0




