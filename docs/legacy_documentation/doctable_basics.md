# `DocTable` Overview

A `DocTable` acts as an object-oriented interface to a single database table. It combines the utility of [`dataclasses`](https://realpython.com/python-data-classes/) to create schemas from simple object definitions and [sqlalchemy](https://docs.sqlalchemy.org/en/14/core/) to create connections and execute queries to a database. It should be easy to convert existing data-oriented objects to database schemas, and use those objects when inserting/retrieving data. 

In this document I'll cover these topics:

1. Creating Schemas
2. Managing Connections
3. Inserting, Deleting, and Selecting
4. Select Queries

You may also want to see the [vignettes](examples/example_nss_1_intro.html) for more examples, the [`DocTable` docs](ref/doctable.DocTable.html) for more information about the class, or the [schema guide](examples/doctable_schema.html) for more information about creating schemas. I also recommend looking examples for [insert, delete](examples/doctable_insert_delete.html), [select](examples/doctable_select.html), and [update](examples/doctable_update.html) methods.


```python
import random
random.seed(0)
import pandas as pd
import numpy as np
from dataclasses import dataclass

import sys
sys.path.append('..')
import doctable
```

# 1. Creating a Database Schema

`DocTable` schemas are created using the `doctable.schema` decorator on a class that uses `doctable.Col` for defaulted parameters. Check out the [schema guide](examples/doctable_schema.html) for more detail about schema classes. Our demonstration class will include three columns: `id`, `name`, and `age`, with an additional `.is_old` property derived from `age` for example.

Note that the `id` column uses the default value `IDCol()` which sets the variable to be the primary key and to auto-increment. Arguments passed to the generic `Col()` function are passed directly to the [sqlalchemy metadata](https://docs.sqlalchemy.org/en/14/core/metadata.html) to direct column creation. See more in the [schema guide](examples/doctable_schema.html).


```python
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col(nullable=False)
    age: int = doctable.Col()

    @property
    def is_old(self):
        return self.age >= 30 # lol
```

We can instantiate a `DocTable` by passing a `target` and `schema` (`Record` in our example) parameters, and I show the resulting schema using `.schema_table()`. Note that the type hints were used to describe column types, and `id` was used as the auto-incremented primary key.


```python
table = doctable.DocTable(target=':memory:', schema=Record)
table.schema_table()
```




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
      <th>name</th>
      <th>type</th>
      <th>nullable</th>
      <th>default</th>
      <th>autoincrement</th>
      <th>primary_key</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>id</td>
      <td>INTEGER</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>name</td>
      <td>VARCHAR</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>age</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



Probably a more common use case will be to subclass `DocTable` to provide some basic definitions.


```python
class RecordTable(doctable.DocTable):
    _tabname_ = 'records'
    _schema_ = Record
    _indices_ = (
        doctable.Index('ind_age', 'age'),
    )
    _constraints_ = (
        doctable.Constraint('check', 'age > 0'),
    )

table = RecordTable(target=':memory:')
table
```




    <__main__.RecordTable at 0x7f5b40325940>



# 2. Maintaining Database Connections

Obviously a big part of working with databases involves managing connections with the database. By default, `DocTable` instances DO NOT maintain persistent connections to the database - instead, they open a connection as-needed when executing a query. Benchmark comparisons show that the cost of creating a connection is so low relative to an actual insertion that this probably the approach for most applications.

Alternatively, there are several ways of working with connections: as a context manager, using the `persistent_conn` constructor parameter, manually calling `open_conn()` and `close_conn()` (not recommended), and manually requesting a connection to execute using your own sqlalchemy or raw sql library queries.

1. As a context manager. Note that the `__enter__` method returns the doctable instance itself, so you can access it using with or without the "as" keyword.


```python
tab = doctable.DocTable(target=':memory:', schema=Record)
print(tab._conn)
with tab as t:
    r = Record(name = 'Devin Cornell', age = 32)
    print(dir(r))
    t.insert_single(Record(name = 'Devin Cornell', age = 32))
    print(t._conn)
    
# alternatively, no need to use "as"
with tab:
    tab.insert_single(Record(name = 'Devin Cornell', age = 32))
    print(tab._conn)
tab.head()
    
```

    None
    ['__annotations__', '__class__', '__dataclass_fields__', '__dataclass_params__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getitem__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__slots__', '__str__', '__subclasshook__', '__wrapped__', '_doctable__age', '_doctable__id', '_doctable__name', '_doctable_as_dict', '_doctable_from_db', '_doctable_get_val', 'age', 'as_dict', 'get_val', 'id', 'is_old', 'name']
    <sqlalchemy.engine.base.Connection object at 0x7f5b40304550>
    <sqlalchemy.engine.base.Connection object at 0x7f5b403141c0>


    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:408: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
      warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')





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
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Devin Cornell</td>
      <td>32</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Devin Cornell</td>
      <td>32</td>
    </tr>
  </tbody>
</table>
</div>



2. Using the constructor argument `persistent_conn`


```python
tab = doctable.DocTable(target=':memory:', schema=Record, persistent_conn=False)
print(tab._conn)
tab = doctable.DocTable(target=':memory:', schema=Record, persistent_conn=True)
tab._conn
```

    None





    <sqlalchemy.engine.base.Connection at 0x7f5b402cd280>



3. Manually calling `.open_conn()` and `.close_conn()`. I recommend using a context manager if you go this route.


```python
tab = doctable.DocTable(target=':memory:', schema=Record)
print(tab._conn)
tab.open_conn()
print(tab._conn)
tab.close_conn()
print(tab._conn)
```

    None
    <sqlalchemy.engine.base.Connection object at 0x7f5b403097c0>
    None


4. grabbing a connection object to execute your own sqlalchemy queries


```python
conn = tab.connect()
conn
```




    <sqlalchemy.engine.base.Connection at 0x7f5b40309550>



# 3. Insert, Delete, and Select

The nature of doctable schema definitions means the easiest way to work with database data is often to use the schema class as a normal dataclass. I recommend the [schema guide](examples/doctable_schema.html) for more detail about the relationship between dataclasses, schema classes, and behavior of the actual database. While the intent behind using dataclasses for database schemas is intuitive and valuable, it can be tricky.

> NOTE!!!: Unlike ORM-based applications, `DocTable` instances do not have any connection to instances of the schema class - they are simply used to encapsulate data to be stored and retrieved in the table. This is why the same object can be inserted multiple times in this example.

Lets start off by creating some record objects and inserting them into the database with `.insert_single()` and `.insert_many()`. In the `Record` constructor here we do not specify the id value - this is because our database schema dictated that it will be automatically incremented by the database - if we omit the value in the constructor, by default it will simply not pass any value to the database at all (this can be changed later though). See that the results of our call to `.head()` shows that the rows were given id values upon insertion.


```python
table = doctable.DocTable(target=':memory:', schema=Record)

o = Record(name='Devin Cornell', age=35)
table.insert_single(o, verbose=True)
table.insert_single(o)
table.insert_many([o, o], verbose=True)
table.head()
```

    DocTable: INSERT OR FAIL INTO _documents_ (id, name, age) VALUES (?, ?, ?)
    DocTable: INSERT OR FAIL INTO _documents_ (id, name, age) VALUES (?, ?, ?)


    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: .insert_many() is depricated: please use .q.insert_multi() or .q.insert_multi_raw()
      warnings.warn(f'.insert_many() is depricated: please use .q.insert_multi() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:408: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
      warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')





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
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Devin Cornell</td>
      <td>35</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Devin Cornell</td>
      <td>35</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Devin Cornell</td>
      <td>35</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>Devin Cornell</td>
      <td>35</td>
    </tr>
  </tbody>
</table>
</div>



Now we use `.select()` to retrieve data from the database. Here we call it with no parameters to simply get all the objects we previously inserted, this time with the id values that the database provided.


```python
results = table.select(verbose=True)
results
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_


    /DataDrive/code/doctable/examples/../doctable/doctable.py:452: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')





    [Record(id=1, name='Devin Cornell', age=35),
     Record(id=2, name='Devin Cornell', age=35),
     Record(id=3, name='Devin Cornell', age=35),
     Record(id=4, name='Devin Cornell', age=35)]



# 4. More Complicated Queries
And, of course, the most important part of any database library is to execute queries. To do this, `DocTable` objects keep track of [sqlalchemy core `MetaData` and `Table` objects](https://docs.sqlalchemy.org/en/14/core/metadata.html) and build queries using the `select()`, `delete()`, `insert()`, and `update()` methods from sqlalchemy core.

First, note that subscripting the table object allows you to access the underlying sqlalchemy `Column` objects, which, as I will show a bit later, can be used to create where conditionals for select and update queries. You can also access specific column data using the `.c` property of the doctable.


```python
table = doctable.DocTable(target=':memory:', schema=Record)

table['id'], table.c.id
```




    (Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False),
     Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False))



As we'll show later, these column objects also have some operators defined such that they can be used to construct complex queries and functions. You can read more about this in the [sqlalchemy operators documentation](https://docs.sqlalchemy.org/en/14/core/operators.html).


```python
table.c.id > 3, table.c.id.in_([1,2]), table.c.age == 4
```




    (<sqlalchemy.sql.elements.BinaryExpression object at 0x7f5b4025cd00>,
     <sqlalchemy.sql.elements.BinaryExpression object at 0x7f5b4025cc70>,
     <sqlalchemy.sql.elements.BinaryExpression object at 0x7f5b4025c8e0>)



You can use these expressions as part of `select()`, `update()`, and `delete()` operations by passing them to the `where` argument.


```python
table.insert_single(Record(name='Devin Cornell', age=35))
table.insert_single(Record(name='Sam Adams', age=250))
table.insert_single(Record(name='Rando', age=500))

table.select(where=table.c.id >= 3, verbose=True)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_ 
    WHERE _documents_.id >= ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '





    [Record(id=3, name='Rando', age=500)]




```python
table.select_first(where=table.c.name=='Devin Cornell', verbose=True)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_ 
    WHERE _documents_.name = ?
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:427: UserWarning: Method .select_first() is depricated. Please use .q.select_first() instead.
      warnings.warn('Method .select_first() is depricated. Please use .q.select_first() instead.')





    Record(id=1, name='Devin Cornell', age=35)



### Select Statements
Now we show how to select data from the table. Use the `.count()` method to check the number of rows. It also accepts some column conditionals to count entries that satisfy a given criteria


```python
table.count(verbose=True), table.count(table['age']>=30, verbose=True)
```

    DocTable: SELECT count(_documents_.id) AS count_1 
    FROM _documents_
     LIMIT ? OFFSET ?
    DocTable: SELECT count(_documents_.id) AS count_1 
    FROM _documents_ 
    WHERE _documents_.age >= ?
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')





    (3, 3)



Use the `.select()` method with no arguments to retrieve all rows of the table. You can also choose to select one or more columns to select.


```python
table.select(verbose=True)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_





    [Record(id=1, name='Devin Cornell', age=35),
     Record(id=2, name='Sam Adams', age=250),
     Record(id=3, name='Rando', age=500)]



By specifying a column name, you can retrieve a list of column values, or by offering a list of data, you can request only those datas.


```python
table.select('name', verbose=True)
```

    DocTable: SELECT _documents_.name 
    FROM _documents_





    ['Devin Cornell', 'Sam Adams', 'Rando']




```python
# note we have no access to the ID column - just name, but still part of Record type.
table.select(['name'], verbose=True)
```

    DocTable: SELECT _documents_.name 
    FROM _documents_





    [Record(name='Devin Cornell'), Record(name='Sam Adams'), Record(name='Rando')]



Accessing a property which was not retrieved from the database will raise an exception.


```python
rec = table.select_first(['name'])
try:
    rec.id
except doctable.RowDataNotAvailableError as e:
    print('This exception was raised:', e)
```

    This exception was raised: The "id" property is not available. This might happen if you did not retrieve the information from a database or if you did not provide a value in the class constructor.


You may also use aggregation functions like `.sum`.


```python
table.select_first(table['age'].sum(), verbose=True)
```

    DocTable: SELECT sum(_documents_.age) AS sum_1 
    FROM _documents_
     LIMIT ? OFFSET ?





    785



The SUM() and COUNT() SQL functions have been mapped to `.sum` and `.count` attributes of columns. Use `as_dataclass=False` if you do retrieve data which does not fit into a `Record` object.


```python
table.select_first([table['age'].sum(),table['age'].count()], verbose=True)
```

    DocTable: SELECT sum(_documents_.age) AS sum_1, count(_documents_.age) AS count_1 
    FROM _documents_
     LIMIT ? OFFSET ?
    DocTable: SELECT sum(_documents_.age) AS sum_1, count(_documents_.age) AS count_1 
    FROM _documents_
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:443: UserWarning: Conversion from row to object failed according to the following error. Please use .q.select_first(..,raw_result=True) next time in the future to avoid this issue. e=RowDataConversionFailed("Conversion from <class 'sqlalchemy.engine.row.LegacyRow'> to <class '__main__.Record'> failed.")
      warnings.warn(f'Conversion from row to object failed according to the following '





    (785, 3)



Alternatively, to see the results as a pandas dataframe, we can use ```.select_df()```.


```python
table.select_df(verbose=True)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_


    /DataDrive/code/doctable/examples/../doctable/doctable.py:420: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
      warnings.warn('Method .select_df() is depricated. Please use .q.select_df() instead.')





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
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Devin Cornell</td>
      <td>35</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Sam Adams</td>
      <td>250</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>Rando</td>
      <td>500</td>
    </tr>
  </tbody>
</table>
</div>



Now we can select specific elements of the db using the ```where``` argument of the ```.select()``` method.


```python
table.select(where=table['age'] >= 1, verbose=True)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_ 
    WHERE _documents_.age >= ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:452: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')





    [Record(id=1, name='Devin Cornell', age=35),
     Record(id=2, name='Sam Adams', age=250),
     Record(id=3, name='Rando', age=500)]




```python
table.select(where=table['id']==3, verbose=True)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age 
    FROM _documents_ 
    WHERE _documents_.id = ?





    [Record(id=3, name='Rando', age=500)]



We can update the results in a similar way, using the ```where``` argument.


```python
table.update({'name':'smartypants'}, where=table['id']==3, verbose=True)
table.select()
```

    DocTable: UPDATE _documents_ SET name=? WHERE _documents_.id = ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:504: UserWarning: Method .update() is depricated. Please use .q.update() instead.
      warnings.warn('Method .update() is depricated. Please use .q.update() instead.')





    [Record(id=1, name='Devin Cornell', age=35),
     Record(id=2, name='Sam Adams', age=250),
     Record(id=3, name='smartypants', age=500)]




```python
print(table['age']*100)
table.update({'age':table['age']*100}, verbose=True)
table.select()
```

    _documents_.age * :age_1
    DocTable: UPDATE _documents_ SET age=(_documents_.age * ?)





    [Record(id=1, name='Devin Cornell', age=3500),
     Record(id=2, name='Sam Adams', age=25000),
     Record(id=3, name='smartypants', age=50000)]



And we can delete elements using the ```.delete()``` method.


```python
table.delete(where=table['id']==3, verbose=True)
table.select()
```

    DocTable: DELETE FROM _documents_ WHERE _documents_.id = ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:509: UserWarning: Method .delete() is depricated. Please use .q.delete() instead.
      warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')





    [Record(id=1, name='Devin Cornell', age=3500),
     Record(id=2, name='Sam Adams', age=25000)]



# Notes on DB Interface
DocTable2 allows you to access columns through direct subscripting, then relies on the power of sqlalchemy column objects to do most of the work of constructing queries. Here are a few notes on their use. For more demonstration, see the example in examples/dt2_select.ipynb


```python
# subscript is used to access underlying sqlalchemy column reference (without querying data)
table['id']
```




    Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False)




```python
# conditionals are applied directly to the column objects (as we'll see with "where" clause)
table['id'] < 3
```




    <sqlalchemy.sql.elements.BinaryExpression object at 0x7f5b4022fc10>




```python
# can also access using .col() method
table.col('id')
```




    Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False)




```python
# to access all column objects (only useful for working directly with sql info)
table.columns
```




    <sqlalchemy.sql.base.ImmutableColumnCollection at 0x7f5b40388db0>




```python
# to access more detailed schema information
table.schema_table()
```




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
      <th>name</th>
      <th>type</th>
      <th>nullable</th>
      <th>default</th>
      <th>autoincrement</th>
      <th>primary_key</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>id</td>
      <td>INTEGER</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>name</td>
      <td>VARCHAR</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>age</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
# If needed, you can also access the sqlalchemy table object using the .table property.
table.table
```




    Table('_documents_', MetaData(bind=Engine(sqlite:///:memory:)), Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False), Column('name', String(), table=<_documents_>, nullable=False), Column('age', Integer(), table=<_documents_>), schema=None)




```python
# the count method is also an easy way to count rows in the database
table.count()
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')





    2




```python
# the print method makes it easy to see the table name and total row count
print(table)
```

    <DocTable (3 cols)::sqlite:///:memory::_documents_>

