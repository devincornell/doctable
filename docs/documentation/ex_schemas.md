# Table Schemas

In this document, I give some examples for defining single and multi-table database schemas in Python. 


```python
import sys
sys.path.append('../')
import doctable
import pprint
```

### Containers and the `table_schema` decorator

The first step in using doctable is to define a _container_ object. Container objects are defined using the `table_schema` decorator, and are used both to define the schema of a database table and to wrap the data for insertion and selection. Container objects act very similar to normal dataclasses - in fact, they actually are dataclasses with additional information needed to create the database table attached. This informaiton is collected at the time when the decorator is used, and thus the decorator serves only to parse the database schema from the class definition, attach that information to the container class, and return the container type as a dataclass.


```python
@doctable.table_schema # equivalent to @doctable.table_schema()
class Container1:
    name: str

ins = doctable.inspect_schema(Container1)
print(ins.table_name())
ins.column_info_df()
```

    Container1





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
  </tbody>
</table>
</div>




```python
@doctable.table_schema(table_name='container2')
class Container2:
    name: str
    age: int
ins = doctable.inspect_schema(Container2)
print(ins.table_name())
ins.column_info_df()
```

    container2





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
      <th>1</th>
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
  </tbody>
</table>
</div>



### Specifying Column Properties

There are two sets of parameters you may adjust to change the behavior of a column: 

+ `ColumnArgs`: adjust the behavior of the generated column. This does not affect the container object, but does affect the database column.

+ `FieldArgs`: adjust the behavior of container attribute by passing arguments to `dataclasses.field()`. This does not affect the database column, but does affect the way the container object can be used.

Both are passed directly to the `Column` function, which, as you can see, simply returns a `dataclasses.field` object with column arguments passed to the `metadata` attribute. Note that by default, the `default` argument is set to `doctable.MISSING`, so the parameter is optional and will be populated with that value. Missing values will be ignored when inserting the object into the database.


```python
doctable.Column(
    column_args=doctable.ColumnArgs(),
    field_args=doctable.FieldArgs(),
)
```




    Field(name=None,type=None,default=MISSING,default_factory=<dataclasses._MISSING_TYPE object at 0x7fc0f9afe590>,init=True,repr=True,hash=None,compare=True,metadata=mappingproxy({'_column_args': ColumnArgs(order=inf, column_name=None, type_kwargs={}, use_type=None, sqlalchemy_type=None, autoincrement=False, nullable=True, unique=None, primary_key=False, index=None, foreign_key=None, default=None, onupdate=None, server_default=None, server_onupdate=None, comment=None, other_kwargs={})}),kw_only=<dataclasses._MISSING_TYPE object at 0x7fc0f9afe590>,_field_type=None)




```python
import datetime

class PhoneNumber(str):
    pass

class Address(str):
    pass

@doctable.table_schema(table_name='container3')
class Container3:
    name: str
    age: int = doctable.Column(field_args=doctable.FieldArgs(init_required=True))
    address: Address = doctable.Column()
    phone: PhoneNumber = doctable.Column()
    
    # this column will appear first in the database, even though this attribute is later
    _id: int = doctable.Column(
        column_args=doctable.ColumnArgs(
            column_name='id', # name of the column in the db (might not want to have an attr called 'id')
            order = 0, # affects the ordering of the columns in the db
            primary_key=True,
            autoincrement=True,
        ),
    )
    
    # doctable will define default and onupdate when inserting into database
    added: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(
            default=datetime.datetime.now, 
            onupdate=datetime.datetime.now
        ),
        field_args = doctable.FieldArgs(
            repr=False, # don't show this field when printing
        )
    )    

doctable.inspect_schema(Container3).column_info_df()
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
      <td>_id</td>
      <td>int</td>
      <td>(0, 4)</td>
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
      <td>address</td>
      <td>String</td>
      <td>address</td>
      <td>Address</td>
      <td>(inf, 2)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>phone</td>
      <td>String</td>
      <td>phone</td>
      <td>PhoneNumber</td>
      <td>(inf, 3)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>5</th>
      <td>added</td>
      <td>DateTime</td>
      <td>added</td>
      <td>datetime</td>
      <td>(inf, 5)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>now</td>
    </tr>
  </tbody>
</table>
</div>



Notice that the string representation does not show the `added` attribute, as specified via `FieldAargs(repr=False)`.


```python
Container3('Devin J. Cornell', 30)
```




    Container3(name='Devin J. Cornell', age=30, address=MISSING, phone=MISSING, _id=MISSING)



### Indices

Indices may be added to a table by passing a dictionary of name, `Index` pairs to the `indices` parameter of the `table_schema` decorator. The arguments are the columns, and any additional keyword arguments may be passed after.


```python
@doctable.table_schema(
    table_name='container4',
    indices = {
        'ind_name': doctable.Index('name'),
        'ind_name_age': doctable.Index('name', 'age', unique=True),
    }
)
class Container4:
    name: str
    age: int

ins = doctable.inspect_schema(Container4)
ins.index_info_df()
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
      <th>columns</th>
      <th>kwargs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ind_name</td>
      <td>name</td>
      <td></td>
    </tr>
    <tr>
      <th>1</th>
      <td>ind_name_age</td>
      <td>name, age</td>
      <td>unique: True</td>
    </tr>
  </tbody>
</table>
</div>



### Constraints

You may pass constraints through the `constraint` parameter of the `table_schema` decorator.

There are several types of constraints you may want to use in your schema. The following methods are thin wrappers over the [SQLAlchemy objects of the same name](https://docs.sqlalchemy.org/en/20/core/constraints.html).

| docs | Constraint | Description |
| --- | --- | --- |
| [link](https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.ForeignKeyConstraint) | `ForeignKey(local_columns, foreign_columns, optional[onupdate], optional[ondelete])` | A foreign key constraint. |
| [link](https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.CheckConstraint) | `CheckConstraint(text, optional[Name])` | A unique constraint. |
| [link](https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.UniqueConstraint) | `UniqueConstraint(*column_names, optional[name])` | A unique constraint. |
| [link](https://docs.sqlalchemy.org/en/20/core/constraints.html#sqlalchemy.schema.PrimaryKeyConstraint) | `PrimaryKeyConstraint(*column_names, optional[name])` | A unique constraint. |


```python
@doctable.table_schema(
    table_name='container5',
    constraints = [
        #doctable.ForeignKey(..), # see multi-table schemas below
        doctable.CheckConstraint('age >= 0', name='check_age'),
        doctable.UniqueConstraint('age', 'name', name='unique_age_name'),
        doctable.PrimaryKeyConstraint('id'),
    ]
)
class Container5:
    id: int # this is the primary key now
    name: str
    age: int
```

### Column Types

The column type resolution works according to the following steps:

1. Check `ColumnArgs.sqlalchemy_type` and use this if it is not `None`.
2. Check if column is foreign key - if it is, ask sqlalchemy to resolve the type
3. Check `ColumnArgs.use_type` and use this if it is provided.
4. Use the provided type hint to resolve the type.

The valid type hints and their sqlalchemy equivalents are listed below.

| Type Hint | SQLAlchemy Type |
| --- | --- |
| `int` | `sqlalchemy.Integer` |
| `float` | `sqlalchemy.Float` |
| `bool` | `sqlalchemy.Boolean` |
| `str` | `sqlalchemy.String` |
| `bytes` | `sqlalchemy.LargeBinary` |
| `datetime.datetime` | `sqlalchemy.DateTime` |
| `datetime.time` | `sqlalchemy.Time` |
| `datetime.date` | `sqlalchemy.Date` |
| `typing.Any` | `sqlalchemy.PickleType` |
| `'datetime.datetime'` | `sqlalchemy.DateTime` |
| `'datetime.time'` | `sqlalchemy.Time` |
| `'datetime.date'` | `sqlalchemy.Date` |
| `'Any'` | `sqlalchemy.PickleType` |

You can get the mappings programatically if needed as well:


```python
doctable.type_mappings()
```




    {int: sqlalchemy.sql.sqltypes.Integer,
     float: sqlalchemy.sql.sqltypes.Float,
     bool: sqlalchemy.sql.sqltypes.Boolean,
     str: sqlalchemy.sql.sqltypes.String,
     bytes: sqlalchemy.sql.sqltypes.LargeBinary,
     datetime.datetime: sqlalchemy.sql.sqltypes.DateTime,
     datetime.time: sqlalchemy.sql.sqltypes.Time,
     datetime.date: sqlalchemy.sql.sqltypes.Date,
     doctable.schema.column.column_types.PickleType: sqlalchemy.sql.sqltypes.PickleType,
     'datetime.datetime': sqlalchemy.sql.sqltypes.DateTime,
     'datetime.time': sqlalchemy.sql.sqltypes.Time,
     'datetime.date': sqlalchemy.sql.sqltypes.Date,
     doctable.schema.column.column_types.JSON: sqlalchemy.sql.sqltypes.JSON}



#### Special Column Types

There are several special column types that can be used in your schemas.

| Type Hint | SQLAlchemy Type | Description |
| --- | --- | --- |
| `doctable.JSON` | `sqlalchemy.JSON` | Calls `json.dumps` on write, `json.loads` on read. |
| `doctable.PickleType` | `sqlalchemy.PickleType` | Calls `pickle.dumps` on write, `pickle.loads` on read. |



```python
import dataclasses
import typing

@dataclasses.dataclass
class Address:
    street: str
    city: str
    state: str
    zip: str

@doctable.table_schema
class Container6:
    name: str
    
    # NOTE: will be serialized as a JSON string in the database
    # notice how we can use a more accurate type hint and still specify
    # the column type using use_type
    other_info: typing.Dict[str, typing.Union[str,int,float]] = doctable.Column(
        column_args=doctable.ColumnArgs(
            use_type=doctable.JSON,
        ),
        field_args=doctable.FieldArgs(default_factory=dict),
    )
    
    # NOTE: will be pickled in the database
    address: Address = doctable.Column(
        column_args=doctable.ColumnArgs(
            use_type=doctable.PickleType,
        )
    )
    
doctable.inspect_schema(Container6).column_info_df()
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
      <th>1</th>
      <td>other_info</td>
      <td>JSON</td>
      <td>other_info</td>
      <td>Dict</td>
      <td>(inf, 1)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>address</td>
      <td>PickleType</td>
      <td>address</td>
      <td>Address</td>
      <td>(inf, 2)</td>
      <td>False</td>
      <td>False</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



Now create a new container object that contains an address for insertion.


```python
new_obj = Container6(
    name = 'Devin J. Cornell', 
    other_info = {'favorite_color': 'blue'},
    address = Address('123 Main St.', 'San Francisco', 'CA', '94122'), 
)
new_obj
```




    Container6(name='Devin J. Cornell', other_info={'favorite_color': 'blue'}, address=Address(street='123 Main St.', city='San Francisco', state='CA', zip='94122'))



Now we open a new database, insert the row, and query it back - you can see that the dict data was converted to json and back again, and the address was converted to pickle data and back again.


```python
core = doctable.ConnectCore.open(':memory:', 'sqlite')
with core.begin_ddl() as ddl:
    tab = ddl.create_table(Container6)

with tab.query() as q:
    q.insert_single(new_obj)

with core.query() as q:
    result = q.select(tab.all_cols())
result.first()
```




    ('Devin J. Cornell', {'favorite_color': 'blue'}, Address(street='123 Main St.', city='San Francisco', state='CA', zip='94122'))



## Multi-table Schemas

The example below shows two linked tables: one for colors, and the other for people. Each person has a favorite color that is constrained by a foriegn key to the colors table. The colors table also has a unique constraint on the color name. I demonstrate use of the `Column` function to describe behavior of columns - specifically the use of `ColumnArgs` to specify additional column features that are not conveyed through type annotations or attribute names. I also show use of the `Index` object for creating indexes, the `UniqueConstraint` object for creating unique constraints, and the `ForeignKey` object for creating foreign key constraints. 

Note that the container object representing the database schema is also a usable `dataclass` that can used like any other container object. In fact, tables created according to this schema can insert these objects directly and will wrap return values issued via select queries.


```python
import datetime

@doctable.table_schema(
    table_name='color',
    constraints = [
        doctable.UniqueConstraint('name'),
    ]
)
class Color:
    name: str
    id: int = doctable.Column(
        column_args=doctable.ColumnArgs(
            primary_key=True,
            autoincrement=True,
        )
    )

# lets say we use this instead of an int
class PersonID(int):
    pass

# add table-level parameters to this decorator
@doctable.table_schema(
    table_name='person',
    indices = {
        'ind_name_birthday': doctable.Index('name', 'birthday', unique=True),
    },
    constraints = [ # these constraints are set on the database
        doctable.CheckConstraint('length(address) > 0'), # cannot have a blank address
        doctable.UniqueConstraint('birthday', 'fav_color'),
        doctable.ForeignKey(['fav_color'], ['color.name'], onupdate='CASCADE', ondelete='CASCADE'),
    ],
    frozen = True, # parameter passed to dataclasses.dataclass
)
class Person:
    name: str
    
    # default value will be "not provided" - good standardization
    address: str = doctable.Column(
        column_args=doctable.ColumnArgs(
            server_default='not provided',
        )
    )
    
    # provided as datetime, set to be indexed
    birthday: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(
            index = True,
        )
    )
    
    # note that this has a foreign key constraint above
    fav_color: str = doctable.Column(
        column_args=doctable.ColumnArgs(
            nullable=False,
        )
    )
    
    id: PersonID = doctable.Column( # standard id column
        column_args=doctable.ColumnArgs(
            order=0, # will be the first column
            primary_key=True,
            autoincrement=True
        ),
    )
    
    # doctable will define default and onupdate when inserting into database
    added: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(
            index=True,
            default=datetime.datetime.utcnow, 
            onupdate=datetime.datetime.utcnow
        )
    )
    
    # this property will not be stored in the database 
    #   - it acts like any other property
    @property
    def age(self):
        return datetime.datetime.now() - self.birthday
    
    
core = doctable.ConnectCore.open(
    target=':memory:', 
    dialect='sqlite'
)
# NOTE: weird error when trying to run this twice after defining containers
with core.begin_ddl() as emitter:
    core.enable_foreign_keys() # NOTE: NEEDED TO ENABLE FOREIGN KEYS
    color_tab = emitter.create_table_if_not_exists(container_type=Color)
    person_tab = emitter.create_table_if_not_exists(container_type=Person)
for col_info in person_tab.inspect_columns():
    print(f'{col_info["name"]}: {col_info["type"]}')
```

    id: INTEGER
    name: VARCHAR
    address: VARCHAR
    birthday: DATETIME
    fav_color: VARCHAR
    added: DATETIME


Insertion into the color table is fairly straightforward.


```python
color_names = ['red', 'green', 'blue']
colors = [Color(name=name) for name in color_names]
with color_tab.query() as q:
    q.insert_multi(colors)
    for c in q.select():
        print(c)
    #print(q.select())
```

    Color(name='red', id=1)
    Color(name='green', id=2)
    Color(name='blue', id=3)


Insertion into the person table is similar, and note that we see an exception if we try to insert a person with a favorite color that is not in the color table.


```python
persons = [
    Person(name='John', birthday=datetime.datetime(1990, 1, 1), fav_color='red'),
    Person(name='Sue', birthday=datetime.datetime(1991, 1, 1), fav_color='green'),
    Person(name='Ren', birthday=datetime.datetime(1995, 1, 1), fav_color='blue'),
]
other_person = Person(
    name='Bob', 
    address='123 Main St', 
    birthday=datetime.datetime(1990, 1, 1), 
    fav_color='other', # NOTE: THIS WILL CAUSE AN ERROR (NOT IN COLOR TABLE)
)

import sqlalchemy.exc

sec_in_one_year = 24*60*60*365
with person_tab.query() as q:
    q.insert_multi(persons, ifnotunique='replace')
    
    try:
        q.insert_single(other_person, ifnotunique='replace')
        print(f'THIS SHOULD NOT APPEAR')
    except sqlalchemy.exc.IntegrityError as e:
        print(f'successfully threw exception: {e}')
    
    for p in q.select():
        print(f'{p.name} ({p.fav_color}): {p.age.total_seconds()//sec_in_one_year:0.0f} y/o')
```

    successfully threw exception: (sqlite3.IntegrityError) FOREIGN KEY constraint failed
    [SQL: INSERT OR REPLACE INTO person (name, address, birthday, fav_color, added) VALUES (?, ?, ?, ?, ?)]
    [parameters: ('Bob', '123 Main St', '1990-01-01 00:00:00.000000', 'other', '2023-11-14 22:17:40.402308')]
    (Background on this error at: https://sqlalche.me/e/20/gkpj)
    John (red): 33 y/o
    Sue (green): 32 y/o
    Ren (blue): 28 y/o


The foreign key works as expected because we set `onupdate`: changing that value in the parent table will update the value in the child table.


```python
with color_tab.query() as q:
    q.update_single(dict(name='reddish'), where=color_tab['name']=='red')
    for c in q.select():
        print(c)
        
with person_tab.query() as q:
    for p in q.select():
        print(f'{p.name} ({p.fav_color}): {p.age.total_seconds()//sec_in_one_year:0.0f} y/o')
```

    Color(name='reddish', id=1)
    Color(name='green', id=2)
    Color(name='blue', id=3)
    John (reddish): 33 y/o
    Sue (green): 32 y/o
    Ren (blue): 28 y/o

