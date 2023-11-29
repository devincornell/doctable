# Dataclass Schema Example
In this vignette I'll show how to use a [Python dataclass](https://realpython.com/python-data-classes/) (introduced in Python 3.7) to specify a schema for a DocTable. The advantage of this schema format is that you can use custom classes to represent each row, and easily convert your existing python objects into a format that it easy to store in a sqlite database.


```python
from datetime import datetime
from pprint import pprint
import pandas as pd
import sys
sys.path.append('..')
import doctable
```

## Basic dataclass usage
For our first example, we show how a basic dataclass object can be used as a DocTable schema. First we create a python dataclass using the `@dataclass` decorator. This object has three members, each defaulted to `None`. We can create this object using the constructor provided by `dataclass`.


```python
from dataclasses import dataclass
@doctable.schema
class User:
    __slots__ = []
    name: str = None
    age: int = None
    height: float = None
User()
```




    User(name=None, age=None, height=None)



And it is relatively easy to create a new doctable using the schema provided by our dataclass `User` by providing the class definition to the `schema` argument. We can see that `DocTable` uses the dataclass schema to create a new table that follows the specified Python datatypes.


```python
db = doctable.DocTable(schema=User, target=':memory:')
db.schema_table()
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
      <td>height</td>
      <td>FLOAT</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



Now we insert several new objects into the table and view them using `DocTable.head()`. Note that the datbase actually inserted the object's defaulted values into the table.


```python
db.insert([User('kevin'), User('tyrone', age=12), User('carlos', age=25, height=6.5)])
db.head()
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
      <th>age</th>
      <th>height</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>kevin</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>tyrone</td>
      <td>12.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>carlos</td>
      <td>25.0</td>
      <td>6.5</td>
    </tr>
  </tbody>
</table>
</div>



Using a normal `select()`, we can extract the results as the original objects. With no parameters, the select statement extracts all columns as they are stored and they exactly match the original data we entered. As expected from the python object, we can access these as properties of the object. Due to the base class `doctable.DocTableRow`, we can also access properties using the `__getitem__` indexing. I'll show why there is a difference btween the two later.


```python
users = db.select()
for user in users:
    print(f"{user.name}:\n\tage: {user.age}\n\theight: {user['height']}")
```

    kevin:
    	age: None
    	height: None
    tyrone:
    	age: 12
    	height: None
    carlos:
    	age: 25
    	height: 6.5


## Example using `doctable.Col`
In this example, we will show how to create a dataclass with functionality that supports more complicated database operations. A key to this approach is to use the `doctable.Col` function as default values for our parameters. Note that when we initialize the object, the default values of all columns except for `name` are set to `EmptyValue`. This is important, because `EmptyValue` will indicate values that are not meant to be inserted into the database or are not retrieved from the database after selecting.


```python
@doctable.schema
class User:
    __slots__ = []
    name: str = doctable.Col()
    age: int = doctable.Col()
    height: float = doctable.Col()
User()
```




    User()



Given that the type specifications are the same as the previous example, we get exactly the same database schema. We insert entries just as before. The `User` data contained `EmptyValue`s, and so that column data was not presented to the database at all - instead, the schema's column defaults were used. Consistent with our schema (not the object defaults, the default values were set to None.


```python
db = doctable.DocTable(schema=User, target=':memory:')
print(db.schema_table())
db.insert([User('kevin'), User('tyrone', age=12), User('carlos', age=25, height=6.5)])
for user in db.select():
    print(f"{user}")
```

         name     type  nullable default autoincrement  primary_key
    0    name  VARCHAR      True    None          auto            0
    1     age  INTEGER      True    None          auto            0
    2  height    FLOAT      True    None          auto            0
    User(name='kevin', age=None, height=None)
    User(name='tyrone', age=None, height=None)
    User(name='carlos', age=None, height=None)


Now let's try to select only a subset of the columns - in this case, 'name' and 'age'.


```python
users = db.select(['name', 'age'])
users[0]
```




    User(name='kevin', age=None)



Note that the user height was set to `EmptyValue`. When we try to access height as an index, we get an error indicating that the data was not retrived in the select statement.


```python
try:
    users[0]['height']
except KeyError as e:
    print(e)
```

    'The column "height" was not retreived in the select statement.'


On the contrary, if we try to access as an attribute, the actual `EmptyValue` object is retrieved. Object properties work as they always have, but indexing into columns will check for errors in the program logic. This implementation shows how dataclass schemas walk the line between regular python objects and database rows, and thus accessing these values can be done differently depending on how much the table entries should be treated like regular objects vs database rows. This is all determined based on how the dataclass columns are configured.


```python
users[0].height
```




    EmptyValue()



## Special column types
Now I'll introduce two special data column types provided by doctable: `IDCol()`, which represents a regular id column in sqlite with autoindex and primary_key parameters set, and `UpdatedCol()`, which records the datetime that an object was added to the database. When we create a new user using the dataclass constructor, these values are set to `EmptyValue`, and are relevant primarily to the database. By setting the `repr` parameter in the `@dataclass` decorator, we can use the `__repr__` of the `DocTableRow` base class, which hides `EmptyValue` columns. This is optional.


```python
from dataclasses import field, fields
@doctable.schema(repr=False)
class User:
    __slots__ = []
    id: int = doctable.IDCol() # shortcut for autoindex, primary_key column.
    updated: datetime = doctable.UpdatedCol() # shortcut for automatically 
    
    name: str = doctable.Col(nullable=False)
    age: int = doctable.Col(None) # accessing sqlalchemy column keywords arguments

user = User(name='carlos', age=15)
user
```




    User(name='carlos', age=15)



And we can see the relevance of those columns by inserting them into the database and selecting them again. You can see from the result of `.head()` that the primary key `id` and the `updated` columns were appropriately filled upon insertion. After selecting, these objects also contain valid values.


```python
db = doctable.DocTable(schema=User, target=':memory:')
print(db.schema_table())
db.insert([User(name='kevin'), User(name='tyrone', age=12), User(name='carlos', age=25)])
db.head()
```

          name      type  nullable default autoincrement  primary_key
    0       id   INTEGER     False    None          auto            1
    1  updated  DATETIME      True    None          auto            0
    2     name   VARCHAR     False    None          auto            0
    3      age   INTEGER      True    None          auto            0





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
      <th>updated</th>
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2021-07-21 19:03:04.550804</td>
      <td>kevin</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2021-07-21 19:03:04.550809</td>
      <td>tyrone</td>
      <td>12.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2021-07-21 19:03:04.550811</td>
      <td>carlos</td>
      <td>25.0</td>
    </tr>
  </tbody>
</table>
</div>



This was just an example of how regular Python dataclass objects can contain additional data which is relevant to the database, but which is otherwise unneeded. After retrieving from database, we can also use `.update()` to modify the entry.


```python
user = db.select_first()
user.age = 10
db.update(user, where=db['id']==user['id'])
db.head()
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
      <th>id</th>
      <th>updated</th>
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2021-07-21 19:03:04.550804</td>
      <td>kevin</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2021-07-21 19:03:04.550809</td>
      <td>tyrone</td>
      <td>12</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2021-07-21 19:03:04.550811</td>
      <td>carlos</td>
      <td>25</td>
    </tr>
  </tbody>
</table>
</div>



We can use the convenience function `update_dataclass()` to update a single row corresponding to the object.


```python
user.age = 11
db.update_dataclass(user)
db.head()
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
      <th>id</th>
      <th>updated</th>
      <th>name</th>
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2021-07-21 19:03:04.550804</td>
      <td>kevin</td>
      <td>11</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2021-07-21 19:03:04.550809</td>
      <td>tyrone</td>
      <td>12</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2021-07-21 19:03:04.550811</td>
      <td>carlos</td>
      <td>25</td>
    </tr>
  </tbody>
</table>
</div>




```python

```


```python

```


```python

```


```python

```
