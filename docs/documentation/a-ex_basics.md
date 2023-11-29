# Introduction

Here I will give an overview of the basic functionality of `doctable`.

I will cover the following topics:

+ Connecting to the database using `ConnectCore`.
+ Defining a database schema using the `table_schema` decorator.
+ Creating the table using the `begin_ddl()` context manager.
+ Inserting values into the database using the `ConnectQuery` and `ConnectTable` interfaces.


```
import sys
sys.path.append('../')
import doctable
import pprint
```

The `ConnectCore` objects acts as the primary starting point for any actions performed on the database. We create a new connection to the datbase using the `.open()` factory method constructor.


```
core = doctable.ConnectCore.open(
    target=':memory:', 
    dialect='sqlite'
)
core
```




    ConnectCore(target=':memory:', dialect='sqlite', engine=Engine(sqlite:///:memory:), metadata=MetaData())



Next we define a very basic schema using the `table_schema` decorator. This decorator is used to create a Container object, which contains information about the database schema and is also a dataclass that can be inserted or retrieved from the database. Read the schema definition examples for more information on creating container objects and database schemas.


```
@doctable.table_schema
class MyContainer0:
    id: int
    name: str
    age: int

doctable.inspect_schema(MyContainer0).column_info_df()
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
      <th>Col Name</th>
      <th>Col Type</th>
      <th>Attr Name</th>
      <th>Hint</th>
      <th>Order</th>
      <th>Primary Key</th>
      <th>Foreign Key</th>
      <th>Index</th>
      <th>Default</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>id</td>
      <td>Integer</td>
      <td>id</td>
      <td>int</td>
      <td>(inf, 0)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>name</td>
      <td>String</td>
      <td>name</td>
      <td>str</td>
      <td>(inf, 1)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>age</td>
      <td>Integer</td>
      <td>age</td>
      <td>int</td>
      <td>(inf, 2)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



We actually connect to the database table using the context manager returned by `.begin_ddl()`. This design is necessary for multi-table schemas, but, because of the readability it provides, I will use it for single-table schemas as well. The method `create_table_if_not_exists` here returns a new instance of `DBTable`. Alternatively, we could reflect a database table, in which we would not be required to provide a schema container.


```
with core.begin_ddl() as emitter:
    tab0 = emitter.create_table_if_not_exists(container_type=MyContainer0)
for ci in core.inspect_columns('MyContainer0'):
    print(ci)
```

    {'name': 'id', 'type': INTEGER(), 'nullable': True, 'default': None, 'primary_key': 0}
    {'name': 'name', 'type': VARCHAR(), 'nullable': True, 'default': None, 'primary_key': 0}
    {'name': 'age', 'type': INTEGER(), 'nullable': True, 'default': None, 'primary_key': 0}


We can perform queries on the database using the `ConnectQuery` interface returned from the `ConnectCore.query()` method. In this case, we insert a new row into the database using the `insert_multi()` method. Not that we will use an alternative interface for inserting container instances into the database.


```
with core.query() as q:
    q.insert_multi(tab0, [
        {'name': 'Devin J. Cornell', 'age': 50},
        {'name': 'Dorothy Andrews', 'age': 49},
    ])
    print(q.select(tab0.all_cols()).all())
```

    [(None, 'Devin J. Cornell', 50), (None, 'Dorothy Andrews', 49)]


To insert container object instances into the table, I instead use the `DBTable.query()` method to generate a `TableQuery` instance. This behaves much like `ConnectQuery` except that returned data will be placed into new container instances and we may insert data from container instances directly.


```
with tab0.query() as q:
    q.insert_single(MyContainer0(id=0, name='John Doe', age=30))
    print(q.select())
```

    [MyContainer0(id=None, name='Devin J. Cornell', age=50), MyContainer0(id=None, name='Dorothy Andrews', age=49), MyContainer0(id=0, name='John Doe', age=30)]


Here I define a more complicated schema. 

+ The standard `id` column is now included. Notice that `order=0` means the column will appear first in the table.
+ The `updated` and `added` attributes have been created to automatically record the time of insertion and update.
+ I added the `birthyear` method to the container type.


```
import datetime
@doctable.table_schema(table_name='mytable1')
class MyContainer1:
    name: str
    age: int
    id: int = doctable.Column(
        column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
    )
    updated: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(default=datetime.datetime.utcnow),
    )
    added: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(
            default=datetime.datetime.utcnow, 
            onupdate=datetime.datetime.utcnow,
        )
    )
    
    def birthyear(self):
        '''Retrieve the birthyear of the person at the time this database entry was added.'''
        try:
            return self.added.year - self.age
        except AttributeError as e:
            raise AttributeError('Cannot calculate birthyear without the added date. '
                'Did you mean to call this on a retrieved container instance?') from e
    
doctable.inspect_schema(MyContainer1).column_info_df()
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
      <th>Col Name</th>
      <th>Col Type</th>
      <th>Attr Name</th>
      <th>Hint</th>
      <th>Order</th>
      <th>Primary Key</th>
      <th>Foreign Key</th>
      <th>Index</th>
      <th>Default</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>id</td>
      <td>Integer</td>
      <td>id</td>
      <td>int</td>
      <td>(0, 2)</td>
      <td>True</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>name</td>
      <td>String</td>
      <td>name</td>
      <td>str</td>
      <td>(inf, 0)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>age</td>
      <td>Integer</td>
      <td>age</td>
      <td>int</td>
      <td>(inf, 1)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>updated</td>
      <td>DateTime</td>
      <td>updated</td>
      <td>datetime</td>
      <td>(inf, 3)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>utcnow</td>
    </tr>
    <tr>
      <th>4</th>
      <td>added</td>
      <td>DateTime</td>
      <td>added</td>
      <td>datetime</td>
      <td>(inf, 4)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>utcnow</td>
    </tr>
  </tbody>
</table>
</div>



We create this table just as we did the one before, and show the new schema using inspection.


```
with core.begin_ddl() as emitter:
    tab1 = emitter.create_table_if_not_exists(container_type=MyContainer1)

for ci in core.inspect_columns('mytable1'):
    print(ci)
```

    {'name': 'id', 'type': INTEGER(), 'nullable': True, 'default': None, 'primary_key': 1}
    {'name': 'name', 'type': VARCHAR(), 'nullable': True, 'default': None, 'primary_key': 0}
    {'name': 'age', 'type': INTEGER(), 'nullable': True, 'default': None, 'primary_key': 0}
    {'name': 'updated', 'type': DATETIME(), 'nullable': True, 'default': None, 'primary_key': 0}
    {'name': 'added', 'type': DATETIME(), 'nullable': True, 'default': None, 'primary_key': 0}


We can create a containser instance just as we did before. Note that `id`, `updated`, and `added` are optionally now because we expect the database to create them.


```
o = MyContainer1(name='John Doe', age=30)
o
```




    MyContainer1(name='John Doe', age=30, id=MISSING, updated=MISSING, added=MISSING)



As expected, calling `.birthyear()` raises an exception because the `added` entry has not been recorded - that will happen at insertion into the db.


```
try:
    o.birthyear()
except AttributeError as e:
    print('error raised:', e)
```

    error raised: Cannot calculate birthyear without the added date. Did you mean to call this on a retrieved container instance?


After inserting the object into the database and retrieving it again, we can see that those previously missing fileds have been populated.


```
with tab1.query() as q:
    q.insert_single(o)
    results = q.select()
results[0]
```




    MyContainer1(name='John Doe', age=30, id=1, updated=datetime.datetime(2023, 11, 16, 17, 40, 7, 684832), added=datetime.datetime(2023, 11, 16, 17, 40, 7, 684836))



And now we can call the `birthyear()` method.


```
results[0].birthyear()
```




    1993



### Conclusion

For more detailed explanations of these topics, see the documentation and API reference provided on the website. Good luck!
