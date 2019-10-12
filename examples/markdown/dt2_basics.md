```python
import random
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
import doctable as dt
```

More details about the schema creation can be found in the folder examples/dt2_schema.py

# Init DocTable2 Object
A DocTable2 instance maintains reference to a database. When constructing, you will typically specify a database file name, a table name, and a database engine (or [dialect - sqlite, mysql, etc](https://docs.sqlalchemy.org/en/13/dialects/)). The default database name (```fname```) is ":memory:", a special keyword that will create a database in memory. I use that for most of the examples. The default ```tabname``` is "_documents_", and unless your applications require multiple tables in the same database, specifying one may not be useful. The default ```engine``` is sqlite, and that may be the easiest to work with most of the time. The ```persistent_conn``` parameter will choose whether your application should maintain an open connection to the database (use this if you want to call ```.update()``` in a ```.select()``` loop), or make a new connection every time you attempt to execute a query (use this if multiple threads might try to access the database at the same time). The ```new_db``` flag should be set to False if you are attempting to access a database but do not want to create one if it does not already exist. This prevents the accidental creation of a new database with no rows if it can't find the one you intended to specify. The ```verbose``` flag might be used for demonstration or debugging: it simply requests that sql commands are printed before being executed. This can also be overridden on a per-transaction basis.

Now, let's create a simple schema and doctable:


```python
schema = (
    ('id','integer',dict(primary_key=True, autoincrement=True)),
    ('name','string', dict(nullable=False)),
    ('age','integer'),
    ('is_old', 'boolean'),
)
db = dt.DocTable2(schema)
print(db)
```

    <DocTable2::_documents_ ct: 0>


You can see from the above that we created a new doctable instance with the specified schema. By printing the object, we can see that the table has no entries. Now, we add some rows one at a time using the ```.insert()``` method.


```python
N = 5
for i in range(N):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    row = {'name':'user_'+str(i), 'age':age, 'is_old':is_old}
    db.insert(row)
print(db)
```

    <DocTable2::_documents_ ct: 5>


Now you can see the doctable has 5 entries. Let's see what they look like. We use the ```.select()``` method with no arguments to retrieve all rows of the table.


```python
db.select()
```




    [(1, 'user_0', 0.2642203445941881, False),
     (2, 'user_1', 0.967644452442394, True),
     (3, 'user_2', 0.2309394848344387, False),
     (4, 'user_3', 0.17800587917544441, False),
     (5, 'user_4', 0.31607298450832433, False)]




```python
db.select('name')
```




    ['user_0', 'user_1', 'user_2', 'user_3', 'user_4']




```python
db.select(['id','name'])
```




    [(1, 'user_0'), (2, 'user_1'), (3, 'user_2'), (4, 'user_3'), (5, 'user_4')]




```python
db.select(db['age'].sum)
```




    [1.9568831455547897]




```python
db.select([db['age'].sum,db['age'].count])
```




    [(1.9568831455547897, 5)]



Alternatively, to see the results as a pandas dataframe, we can use ```.select_df()```.


```python
db.select_df()
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
      <th>name</th>
      <th>age</th>
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>user_0</td>
      <td>0.546092</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>0.924233</td>
      <td>True</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>user_2</td>
      <td>0.854421</td>
      <td>True</td>
    </tr>
    <tr>
      <td>3</td>
      <td>4</td>
      <td>user_3</td>
      <td>0.636434</td>
      <td>True</td>
    </tr>
    <tr>
      <td>4</td>
      <td>5</td>
      <td>user_4</td>
      <td>0.906223</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



Now we can select specific elements of the db using the ```where``` argument of the ```.select()``` method.


```python
db.select(where=db['is_old']==True)
```




    [(1, 'user_0', 0.5460915367661396, True),
     (2, 'user_1', 0.9242334727101083, True),
     (3, 'user_2', 0.8544210737656606, True),
     (4, 'user_3', 0.6364344086051639, True),
     (5, 'user_4', 0.9062232522850379, True)]




```python
db.select(where=db['id']==3)
```




    [(3, 'user_2', 0.8544210737656606, True)]



We can update the results in a similar way, using the ```where``` argument.


```python
db.update({'name':'smartypants'}, where=db['id']==3)
db.select()
```




    [(1, 'user_0', 0.5460915367661396, True),
     (2, 'user_1', 0.9242334727101083, True),
     (3, 'smartypants', 0.8544210737656606, True),
     (4, 'user_3', 0.6364344086051639, True),
     (5, 'user_4', 0.9062232522850379, True)]




```python
db.update({'age':db['age']*100})
db.select()
```




    [(1, 'user_0', 54.609153676613964, True),
     (2, 'user_1', 92.42334727101083, True),
     (3, 'smartypants', 85.44210737656606, True),
     (4, 'user_3', 63.643440860516385, True),
     (5, 'user_4', 90.62232522850378, True)]



And we can delete elements using the ```.delete()``` method.


```python
db.delete(where=db['id']==3)
db.select()
```




    [(1, 'user_0', 54.609153676613964, True),
     (2, 'user_1', 92.42334727101083, True),
     (4, 'user_3', 63.643440860516385, True),
     (5, 'user_4', 90.62232522850378, True)]



# Notes on DB Interface
DocTable2 allows you to access columns through direct subscripting, then relies on the power of sqlalchemy column objects to do most of the work of constructing queries. Here are a few notes on their use. For more demonstration, see the example in examples/dt2_select.ipynb


```python
# subscript is used to access underlying sqlalchemy column reference (without querying data)
db['id']
```




    Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False)




```python
# conditionals are applied directly to the column objects (as we'll see with "where" clause)
db['id'] < 3
```




    <sqlalchemy.sql.elements.BinaryExpression object at 0x7f9ca322a5f8>




```python
# can also access using .col() method
db.col('id')
```




    Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False)




```python
# to access all column objects (only useful for working directly with sql info)
db.columns
```




    <sqlalchemy.sql.base.ImmutableColumnCollection at 0x7f9ca3298798>




```python
# to access more detailed schema information
db.schemainfo
```




    [{'name': 'id',
      'type': INTEGER(),
      'nullable': False,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 1},
     {'name': 'name',
      'type': VARCHAR(),
      'nullable': False,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 0},
     {'name': 'age',
      'type': INTEGER(),
      'nullable': True,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 0},
     {'name': 'is_old',
      'type': BOOLEAN(),
      'nullable': True,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 0}]




```python
# If needed, you can also access the sqlalchemy table object using the .table property.
db.table
```




    Table('_documents_', MetaData(bind=None), Column('id', Integer(), table=<_documents_>, primary_key=True, nullable=False), Column('name', String(), table=<_documents_>, nullable=False), Column('age', Integer(), table=<_documents_>), Column('is_old', Boolean(), table=<_documents_>), schema=None)




```python
# the count method is also an easy way to count rows in the database
db.count()
```




    4




```python
# the print method makes it easy to see the table name and total row count
print(db)
```

    <DocTable2::_documents_ ct: 4>


# Type Mappings
DocTable2 provides a simplified interface into the [SQLAlchemy core](https://docs.sqlalchemy.org/en/13/core/) package component (not the object-relational mapping component). With this interface DocTable2 is able to provide an object-oriented interface to execute SQL commands. This package simplifies that interface by working with the various objects within the class, allowing the user to create schemas and perform queries without working with the hundreds of classes required by SQLAlchemy core.

Because of this, it is important to note the interface between them. The first is the type map used to set up the schema. The DocTable2 constructor provides a schema interface which accepts strings as types, so the type map appears here:


```python
dt.DocTable2._type_map
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
     'pickle': sqlalchemy.sql.sqltypes.PickleType,
     'smallinteger': sqlalchemy.sql.sqltypes.SmallInteger,
     'string': sqlalchemy.sql.sqltypes.String,
     'text': sqlalchemy.sql.sqltypes.Text,
     'time': sqlalchemy.sql.sqltypes.Time,
     'unicode': sqlalchemy.sql.sqltypes.Unicode,
     'unicodetext': sqlalchemy.sql.sqltypes.UnicodeText,
     'tokens': doctable.coltypes.TokensType,
     'subdocs': doctable.coltypes.SubdocsType}



It is often also important to add constraints to schemas, and I've also provided a string-mapping for each constraint type.


```python
dt.DocTable2._constraint_map
```




    {'unique_constraint': sqlalchemy.sql.schema.UniqueConstraint,
     'check_constraint': sqlalchemy.sql.schema.CheckConstraint,
     'primarykey_constraint': sqlalchemy.sql.schema.PrimaryKeyConstraint,
     'foreignkey_constraint': sqlalchemy.sql.schema.ForeignKeyConstraint,
     'index': sqlalchemy.sql.schema.Index}


