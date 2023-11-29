# DocTable Schemas
Your database table column names and types come from a schema class defined using the `@doctable.schema` decorator. In addition to providing a schema definition, this class can be used to encapsulate data when inserting or retrieving from the database. 

At its most basic, your schema class operates like a [dataclass](https://realpython.com/python-data-classes/) that uses slots for efficiency and allows for custom methods that will not affect the database schema.


```python
from datetime import datetime
from pprint import pprint
import pandas as pd

import sys
sys.path.append('..')
import doctable
```

# Introduction

This is an example of a basic doctable schema. Note the use of the decorator `@doctable.schema`, the inclusion of `__slots__ = []`, and the type hints of the member variables - I will explain each of these later in this document.

This class represents a database schema that includes two columns: `name` (an `int`) and `age` (a `str`).


```python
@doctable.schema
class Record:
    __slots__ = []
    name: str
    age: int
```

The schema class definition is then provided to the doctable constructor to create the database table. Here we create an in-memory sqlite table and show the schema resulting from our custom class. Note that doctable automatically inferred that `name` should be a `VARCHAR` and `age` should be an `INTEGER` based on the provided type hints.


```python
# the schema that would result from this dataclass:
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
      <td>name</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
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



We can also use the schema class to insert data into our `DocTable`. We simply create a new `Record` and pass it to the `DocTable.insert()` method. Using `.head()`, we see the contents of the database so far. Note that you may also pass a dictionary to insert data - this is just one way of inserting data.


```python
new_record = Record(name='Devin Cornell', age=30)
print(new_record)
table.insert(new_record)
table.head()
```

    Record(name='Devin Cornell', age=30)





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
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Devin Cornell</td>
      <td>30</td>
    </tr>
  </tbody>
</table>
</div>



And perhaps more usefully, we can use it to encapsulate results from `.select()` queries. Note that the returned object is exactly the same as the one we put in. Slot classes are more memory-efficient than dictionaries for storing data, but there is cpu time overhead from inserting that data into the slots.


```python
first_record = table.select_first()
print(first_record)
```

    Record(name='Devin Cornell', age=30)


But, of course, the data can be returned in its raw format by passing the parameter `as_dataclass=False`.


```python
first_record = table.select_first(as_dataclass=False)
print(first_record)
```

    ('Devin Cornell', 30)


# The `doctable.schema` Decorator

The `@doctable.schema` decorator does the work to convert your custom class into a schema class. It transforms your schema class in three ways:

1. **create slots**: First, [slot](https://docs.python.org/3/reference/datamodel.html#slots) variable names will be added to `__slots__` automatically based on the fields in your class definition. This is why the default functionality requires you to add `__slots__ = []` with no variable names. You may also turn slots off by passing `require_slots=False` to the decorator (i.e. `@doctable.schema(require_slots=False)`), otherwise an exception will be raised.

2. **convert to dataclass**: Second, your schema class will be converted to a [dataclass](https://realpython.com/python-data-classes/) that generates `__init__`, `__repr__`, and other boilerplate methods meant for classes that primarily store data. Any keyword arguments passed to the `schema` decorator, with the exception of `require_slots`, will be passed directly to the `@dataclasses.dataclass` decorator so you have control over the dataclass definition.

3. **inherit from `DocTableSchema`**: Lastly, your schema class will inherit from `doctable.DocTableSchema`, which provides additional accessors that are used for storage in a `DocTable` and fine-grained control over retreived data. More on this later.


Column names and types will be inferred from the type hints in your schema class definition. Because `DocTable` is built on [sqlalchemy core](https://docs.sqlalchemy.org/en/14/core/), all fields will eventually be converted to [`sqlalchemy` column objects](https://docs.sqlalchemy.org/en/13/core/type_basics.html) and added to the DocTable metadata. This table shows the type mappings implemented in doctable:


```python
doctable.python_to_slqlchemy_type
```




    {int: sqlalchemy.sql.sqltypes.Integer,
     float: sqlalchemy.sql.sqltypes.Float,
     str: sqlalchemy.sql.sqltypes.String,
     bool: sqlalchemy.sql.sqltypes.Boolean,
     datetime.datetime: sqlalchemy.sql.sqltypes.DateTime,
     datetime.time: sqlalchemy.sql.sqltypes.Time,
     datetime.date: sqlalchemy.sql.sqltypes.Date,
     doctable.textmodels.parsetreedoc.ParseTreeDoc: doctable.schemas.custom_coltypes.ParseTreeDocFileType}



For example, see this example of the most basic possible schema class that can be used to create a doctable. We use static defaulted parameters and type hints including `str`, `int`, `datetime`, and `Any`, which you can see are converted to `VARCHAR`, `INTEGER`, `DATETIME`, and `BLOB` column types, respectively. `BLOB` was used because the provided type hint `Any` has no entry in the above table.


```python
from typing import Any
import datetime

@doctable.schema
class Record:
    __slots__ = []
    name: str = None
    age: int = None
    time: datetime.datetime = None
    friends: Any = None

# the schema that would result from this dataclass:
doctable.DocTable(target=':memory:', schema=Record).schema_table()
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
      <td>name</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>age</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>time</td>
      <td>DATETIME</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>friends</td>
      <td>BLOB</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



You can see that this class operates much like a regular dataclass with slots. Thus, these defaulted parameters are applied in the constructor of the schema class, and _NOT_ as the default value in the database schema.


```python
Record('Devin Cornell', 30)
```




    Record(name='Devin Cornell', age=30, time=None, friends=None)



# Use `doctable.Col` For More Control Over Schema Creation

Using `doctable.Col()` as a default value in the schema class definition can give you more control over schema definitions. 

Firstly, this function returns a dataclass [`field`](https://docs.python.org/3/library/dataclasses.html#dataclasses.field) object that can be used to set parameters like `default_factory` or `compare` as used by the dataclass. Pass arguments meant for `field` through the `Col` parameter `field_kwargs=dict(..)`. Other data passed to `Col` will be used to create the `DocTable` schema, which is stored as metadata inside the `field`.

This example shows how `Col` can be used to set some parameters meant for `field`. These will affect your schema class behavior without affecting the produced DocTable schema.


```python
@doctable.schema
class Record:
    __slots__ = []
    name: str = doctable.Col()
    age: int = doctable.Col(field_kwargs=dict(default_factory=list, compare=True))

Record()
```




    Record(age=[])



`Col` also allows you to explicitly specify a column type using a string, sqlalchemy type definition, or sqlalchemy instance passed to `column_type`. You can then pass arguments meant for the sqlalchemy type constructor through `type_kwargs`. You may also use `type_kwargs` with the column type inferred from the type hint.


```python
import sqlalchemy

@doctable.schema
class Record:
    __slots__ = []
    
    # providing only the type as first argument
    age: int = doctable.Col(sqlalchemy.BigInteger)

    # these are all quivalent
    name1: str = doctable.Col(type_kwargs=dict(length=100)) # infers type from type hint
    name2: str = doctable.Col(sqlalchemy.String, type_kwargs=dict(length=100)) # accepts provided type sqlalchemy.String, pass parameters through type_kwargs
    name3: str = doctable.Col(sqlalchemy.String(length=100)) # accepts type instance (no need for type_kwargs this way)
    name4: str = doctable.Col('string', type_kwargs=dict(length=100))
    

# the schema that would result from this dataclass:
doctable.DocTable(target=':memory:', schema=Record).schema_table()
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
      <td>age</td>
      <td>BIGINT</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>name1</td>
      <td>VARCHAR(100)</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>name2</td>
      <td>VARCHAR(100)</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>name3</td>
      <td>VARCHAR(100)</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>name4</td>
      <td>VARCHAR(100)</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



A full list of string -> sqlalchemy type mappings is shown below:


```python
doctable.string_to_sqlalchemy_type
```




    {'biginteger': sqlalchemy.sql.sqltypes.BigInteger,
     'boolean': sqlalchemy.sql.sqltypes.Boolean,
     'date': sqlalchemy.sql.sqltypes.Date,
     'datetime': sqlalchemy.sql.sqltypes.DateTime,
     'enum': sqlalchemy.sql.sqltypes.Enum,
     'float': sqlalchemy.sql.sqltypes.Float,
     'integer': sqlalchemy.sql.sqltypes.Integer,
     'interval': sqlalchemy.sql.sqltypes.Interval,
     'largebinary': sqlalchemy.sql.sqltypes.LargeBinary,
     'numeric': sqlalchemy.sql.sqltypes.Numeric,
     'smallinteger': sqlalchemy.sql.sqltypes.SmallInteger,
     'string': sqlalchemy.sql.sqltypes.String,
     'text': sqlalchemy.sql.sqltypes.Text,
     'time': sqlalchemy.sql.sqltypes.Time,
     'unicode': sqlalchemy.sql.sqltypes.Unicode,
     'unicodetext': sqlalchemy.sql.sqltypes.UnicodeText,
     'json': doctable.schemas.custom_coltypes.JSONType,
     'pickle': doctable.schemas.custom_coltypes.CpickleType,
     'parsetree': doctable.schemas.custom_coltypes.ParseTreeDocFileType,
     'picklefile': doctable.schemas.custom_coltypes.PickleFileType,
     'textfile': doctable.schemas.custom_coltypes.TextFileType}



Finally, `Col` allows you to pass keyword arguments directly to the sqlalchemy `Column` constructor. This includes flags like `primary_key` or `default`, which are both used to construct the database schema but do not affect the python dataclass. Note that I recreated the classic `id` column below.


```python
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.Col(primary_key=True, autoincrement=True)
    age: int = doctable.Col(nullable=False)
    name: str = doctable.Col(default='MISSING_NAME')

# the schema that would result from this dataclass:
doctable.DocTable(target=':memory:', schema=Record).schema_table()
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
      <td>age</td>
      <td>INTEGER</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>name</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



I also included some shortcut `Col` functions like `IDCol`, `AddedCol`, and `UpdatedCol` - see below.


```python
import datetime

@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol() # auto-increment primary key
    added: datetime.datetime = doctable.AddedCol() # record when row was added
    updated: datetime.datetime = doctable.UpdatedCol() # record when row was updated

doctable.DocTable(target=':memory:', schema=Record).schema_table()
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
      <td>added</td>
      <td>DATETIME</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>updated</td>
      <td>DATETIME</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



In this way, `Col` allows you to give fine-grained control to both the schema class behavior and the sql schema definition.

# Working With Schema Objects

Using `Col` default parameters also has some additional side effects, primarily due to the inherited class `DocTableSchema`. Among other things, the `Col` method defines the default dataclass value to be a `doctable.EmptyValue()` object, which is essentially a placeholder for data that was not inserted into the class upon construction. The `__repr__` defined in `DocTableSchema` dictates that member objects containing this value not appear when printing the class, and furthermore, member variables with the value `EmptyValue()` will not be provided in the database insertion. This means that the database schema is allowed to use its own default value - an effect which is most obviously useful when inserting an object that does not have an `id` or other automatically provided values.

The example below shows the `new_record.id` contains `EmptyValue()` as a default, and that the `id` column is not included in the insert query - only `name`.


```python
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()

new_record = Record(name='Devin Cornell')
print(new_record)
try:
    print(new_record.id)
except doctable.DataNotAvailableError:
    print(f'exception was raised')

table = doctable.DocTable(target=':memory:', schema=Record, verbose=True)
table.insert(new_record)
table.head()
```

    Record(name='Devin Cornell')
    exception was raised
    DocTable: INSERT OR FAIL INTO _documents_ (name) VALUES (?)
    DocTable: SELECT _documents_.id, _documents_.name 
    FROM _documents_
     LIMIT ? OFFSET ?





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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Devin Cornell</td>
    </tr>
  </tbody>
</table>
</div>



Yet when we go to retrieve the inserted data, we can see that the value has been replaced by the defaulted value in the database. This is a useful feature if your pipeline involves the insertion of schema objects directly (as opposed to inserting dictionaries for each row).


```python
table.select_first(verbose=False)
```




    Record(id=1, name='Devin Cornell')



The `EmptyValue()` feature is also useful when issuing select queries involving only a subset of columns. See here we run a select query where we just retrieve the name data, yet the result is still stored in a `Record` object.


```python
returned_record = table.select_first(['name'], verbose=False)
print(returned_record)
```

    Record(name='Devin Cornell')


To avoid working with `EmptyValue()` objects directly, it is recommended that you use the `__getitem__` string subscripting to access column data. When using this subscript, the schema object will raise an exception if the returned value is an `EmptyValue()`.


```python
try:
    returned_record.id
except doctable.DataNotAvailableError as e:
    print(e)
```

    The "id" property is not available. This might happen if you did not retrieve the information from a database or if you did not provide a value in the class constructor.


# Indices and Constraints

Indices and constraints are provided to the `DocTable` constructor or definition, as it is not part of the schema class. Here I create custom schema and table definitions where the table has some defined indices and constraints. `doctable.Index` is really just a direct reference to `sqlalchemy.Index`, and `doctable.Constraint` is a mapping to an sqlalchemy constraint type, with the first argument indicating which one.


```python
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col()
    age: int = doctable.Col()

class RecordTable(doctable.DocTable):
    _tabname_ = 'records'
    _schema_ = Record

    # table indices
    _indices_ = (
        doctable.Index('name_index', 'name'),
        doctable.Index('name_age_index', 'name', 'age', unique=True),
    )
    
    # table constraints
    _constraints_ = (
        doctable.Constraint('unique', 'name', 'age', name='name_age_constraint'),
        doctable.Constraint('check', 'age > 0', name='check_age'),
    )

table = RecordTable(target=':memory:')
```

And we can see that the constraints are working when we try to insert a record where age is less than 1.


```python
try:
    table.insert(Record(age=-1))
except sqlalchemy.exc.IntegrityError as e:
    print(e)
```

    (sqlite3.IntegrityError) CHECK constraint failed: check_age
    [SQL: INSERT OR FAIL INTO records (age) VALUES (?)]
    [parameters: (-1,)]
    (Background on this error at: http://sqlalche.me/e/13/gkpj)


This is a full list of the mappings between constraint names and the associated sqlalchemy objects.


```python
doctable.constraint_lookup
```




    {'check': sqlalchemy.sql.schema.CheckConstraint,
     'unique': sqlalchemy.sql.schema.UniqueConstraint,
     'primarykey': sqlalchemy.sql.schema.PrimaryKeyConstraint,
     'foreignkey': sqlalchemy.sql.schema.ForeignKeyConstraint}



# Conclusions

In this guide, I tried to show some exmaples and give explanations for the ways that schema classes can be used to create doctables. The design is fairly efficent and flexible, and brings a more object-focused approach compared to raw sql queries without the overhead of ORM.
