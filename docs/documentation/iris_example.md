```python
from __future__ import annotations
import pprint
import pandas as pd
import sqlalchemy

import sys
sys.path.append('../')
import doctable
```

The iris dataset is simply a list of flowers with information about the sepal, petal, and species.


```python
iris_df = pd.read_csv('https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv')
iris_df.head()
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
      <th>sepal_length</th>
      <th>sepal_width</th>
      <th>petal_length</th>
      <th>petal_width</th>
      <th>species</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>5.1</td>
      <td>3.5</td>
      <td>1.4</td>
      <td>0.2</td>
      <td>setosa</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4.9</td>
      <td>3.0</td>
      <td>1.4</td>
      <td>0.2</td>
      <td>setosa</td>
    </tr>
    <tr>
      <th>2</th>
      <td>4.7</td>
      <td>3.2</td>
      <td>1.3</td>
      <td>0.2</td>
      <td>setosa</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4.6</td>
      <td>3.1</td>
      <td>1.5</td>
      <td>0.2</td>
      <td>setosa</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5.0</td>
      <td>3.6</td>
      <td>1.4</td>
      <td>0.2</td>
      <td>setosa</td>
    </tr>
  </tbody>
</table>
</div>



Start by opening a connection to the database with a `ConnectCore` object. This object maintains the sqlalchemy metatdata, engine, and connections and is used to access all objects representing tables, queries, and more.


```python
core = doctable.ConnectCore.open(
    target=':memory:', # use a filename for a sqlite to write to disk
    dialect='sqlite',
    echo=True,
)
core
```




    ConnectCore(target=':memory:', dialect='sqlite', engine=Engine(sqlite:///:memory:), metadata=MetaData())



Define a table using the `table_schema` decorator and listing attributes as you would a dataframe. To give more detail about a column, you can set the default value to `Column()`, which accepts `FieldArgs` to control the behavior of the dataframe container object, and `ColumnArgs()` to control behavior related to the database schema.


```python
import datetime

@doctable.table_schema(table_name='iris', slots=True)
class Iris:
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    species: str
    
    id: int = doctable.Column(
        column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
    )
    updated: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(default=datetime.datetime.utcnow),
    )
    added: datetime.datetime = doctable.Column(
        column_args=doctable.ColumnArgs(
            default=datetime.datetime.utcnow, 
            onupdate=datetime.datetime.utcnow
        )
    )
    
    @classmethod
    def from_row(cls, row: pd.Series):
        return cls(**row)

Iris(sepal_length=1, sepal_width=2, petal_length=3, petal_width=4, species='setosa')
```




    Iris(sepal_length=1, sepal_width=2, petal_length=3, petal_width=4, species='setosa', id=MISSING, updated=MISSING, added=MISSING)



We can start by creating new container object instances using the factory method constructor we created.


```python
irises = [Iris.from_row(row) for _, row in iris_df.iterrows()]
print(irises[0])
```

    Iris(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species='setosa', id=MISSING, updated=MISSING, added=MISSING)


Use the `begin_ddl()` context manager to create database tables.


```python
with core.begin_ddl() as emitter:
    itab = emitter.create_table_if_not_exists(Iris)
itab.inspect_columns()
```

    2023-11-07 18:23:30,147 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 18:23:30,154 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("species")
    2023-11-07 18:23:30,156 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 18:23:30,156 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("iris_entry")
    2023-11-07 18:23:30,157 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 18:23:30,158 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("iris")
    2023-11-07 18:23:30,159 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 18:23:30,160 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("iris")
    2023-11-07 18:23:30,160 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 18:23:30,162 INFO sqlalchemy.engine.Engine 
    CREATE TABLE iris (
    	id INTEGER, 
    	added DATETIME, 
    	petal_length FLOAT, 
    	petal_width FLOAT, 
    	sepal_length FLOAT, 
    	sepal_width FLOAT, 
    	species VARCHAR, 
    	updated DATETIME, 
    	PRIMARY KEY (id)
    )
    
    
    2023-11-07 18:23:30,163 INFO sqlalchemy.engine.Engine [no key 0.00088s] ()
    2023-11-07 18:23:30,164 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-07 18:23:30,165 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 18:23:30,171 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("iris")
    2023-11-07 18:23:30,172 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 18:23:30,173 INFO sqlalchemy.engine.Engine ROLLBACK





    [{'name': 'id',
      'type': INTEGER(),
      'nullable': True,
      'default': None,
      'primary_key': 1},
     {'name': 'added',
      'type': DATETIME(),
      'nullable': True,
      'default': None,
      'primary_key': 0},
     {'name': 'petal_length',
      'type': FLOAT(),
      'nullable': True,
      'default': None,
      'primary_key': 0},
     {'name': 'petal_width',
      'type': FLOAT(),
      'nullable': True,
      'default': None,
      'primary_key': 0},
     {'name': 'sepal_length',
      'type': FLOAT(),
      'nullable': True,
      'default': None,
      'primary_key': 0},
     {'name': 'sepal_width',
      'type': FLOAT(),
      'nullable': True,
      'default': None,
      'primary_key': 0},
     {'name': 'species',
      'type': VARCHAR(),
      'nullable': True,
      'default': None,
      'primary_key': 0},
     {'name': 'updated',
      'type': DATETIME(),
      'nullable': True,
      'default': None,
      'primary_key': 0}]



## Running Queries

### General Queries

Use the `query()` method of `ConnectCore` to perform queries using the doctable interface.


```python
with core.query() as q:
    q.delete(itab, all=True)
    q.insert_single(itab, {
        'sepal_length': 1,'sepal_width': 2,'petal_length': 3,'petal_width': 4,'species': 'setosa'
    })
    print(q.insert_multi.__doc__)
    q.insert_multi(itab, [
        {'sepal_length': 1, 'sepal_width': 2, 'petal_length': 3, 'petal_width': 4, 'species': 'setosa'},
        {'sepal_length': 1, 'sepal_width': 2, 'petal_length': 3, 'petal_width': 4, 'species': 'setosa'},
    ])
    print(q.select(itab).fetchall())
```

    2023-11-07 15:57:55,319 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,320 INFO sqlalchemy.engine.Engine DELETE FROM iris
    2023-11-07 15:57:55,321 INFO sqlalchemy.engine.Engine [generated in 0.00228s] ()
    2023-11-07 15:57:55,325 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO iris (added, petal_length, petal_width, sepal_length, sepal_width, species, updated) VALUES (?, ?, ?, ?, ?, ?, ?)
    2023-11-07 15:57:55,326 INFO sqlalchemy.engine.Engine [generated in 0.00199s] ('2023-11-07 20:57:55.324953', 3.0, 4.0, 1.0, 2.0, 'setosa', '2023-11-07 20:57:55.324955')
    Insert multiple rows into the database using executemany-style 
                parameter binding.
            
    2023-11-07 15:57:55,328 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO iris (added, petal_length, petal_width, sepal_length, sepal_width, species, updated) VALUES (?, ?, ?, ?, ?, ?, ?)
    2023-11-07 15:57:55,329 INFO sqlalchemy.engine.Engine [generated in 0.00088s] [('2023-11-07 20:57:55.328713', 3.0, 4.0, 1.0, 2.0, 'setosa', '2023-11-07 20:57:55.328715'), ('2023-11-07 20:57:55.328719', 3.0, 4.0, 1.0, 2.0, 'setosa', '2023-11-07 20:57:55.328720')]
    2023-11-07 15:57:55,332 INFO sqlalchemy.engine.Engine SELECT iris.id, iris.added, iris.petal_length, iris.petal_width, iris.sepal_length, iris.sepal_width, iris.species, iris.updated 
    FROM iris
    2023-11-07 15:57:55,333 INFO sqlalchemy.engine.Engine [generated in 0.00102s] ()
    [(1, datetime.datetime(2023, 11, 7, 20, 57, 55, 324953), 3.0, 4.0, 1.0, 2.0, 'setosa', datetime.datetime(2023, 11, 7, 20, 57, 55, 324955)), (2, datetime.datetime(2023, 11, 7, 20, 57, 55, 328713), 3.0, 4.0, 1.0, 2.0, 'setosa', datetime.datetime(2023, 11, 7, 20, 57, 55, 328715)), (3, datetime.datetime(2023, 11, 7, 20, 57, 55, 328719), 3.0, 4.0, 1.0, 2.0, 'setosa', datetime.datetime(2023, 11, 7, 20, 57, 55, 328720))]
    2023-11-07 15:57:55,334 INFO sqlalchemy.engine.Engine COMMIT


Use `cols()` or `__call__()` to return a list of column objects associated with the given table. Column objects also have bound operators such as `sum()`, `max()`, and `distinct()` (see comment below for more).


```python
with core.query() as q:
    # use table.cols to specify which columns to select
    columns = itab.cols('sepal_length', 'sepal_width')
    pprint.pprint(q.select(columns).fetchall())
    
    # use subscript to specify table for each column. use for table joins
    columns = [itab['sepal_length'], itab['sepal_width']]
    results = q.select(columns).fetchall()
    pprint.pprint(results)
    
    # use .sum(), .min(), .max(), .count(), .sum(), and .unique() to specify aggregate functions
    columns = [itab['species'].distinct()]
    result = q.select(columns).scalars()
    pprint.pprint(f'{result=}')
    
    # use in conjunction with group_by to specify groupings
    columns = [itab['sepal_length'].sum()]
    result = q.select(columns, group_by=[itab['species']]).scalar_one()
    pprint.pprint(f'{result=}')
```

    2023-11-07 15:57:55,371 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,372 INFO sqlalchemy.engine.Engine SELECT iris.sepal_length, iris.sepal_width 
    FROM iris
    2023-11-07 15:57:55,375 INFO sqlalchemy.engine.Engine [generated in 0.00435s] ()
    [(1.0, 2.0), (1.0, 2.0), (1.0, 2.0)]
    2023-11-07 15:57:55,377 INFO sqlalchemy.engine.Engine SELECT iris.sepal_length, iris.sepal_width 
    FROM iris
    2023-11-07 15:57:55,377 INFO sqlalchemy.engine.Engine [cached since 0.006684s ago] ()
    [(1.0, 2.0), (1.0, 2.0), (1.0, 2.0)]
    2023-11-07 15:57:55,380 INFO sqlalchemy.engine.Engine SELECT distinct(iris.species) AS distinct_1 
    FROM iris
    2023-11-07 15:57:55,381 INFO sqlalchemy.engine.Engine [generated in 0.00088s] ()
    'result=<sqlalchemy.engine.result.ScalarResult object at 0x7f40935dc730>'
    2023-11-07 15:57:55,383 INFO sqlalchemy.engine.Engine SELECT sum(iris.sepal_length) AS sum_1 
    FROM iris GROUP BY iris.species
    2023-11-07 15:57:55,385 INFO sqlalchemy.engine.Engine [generated in 0.00185s] ()
    'result=3.0'
    2023-11-07 15:57:55,386 INFO sqlalchemy.engine.Engine COMMIT


#### Table-specific Queries

Use the `query()` method on a table to reference column names as strings and wrap results in container instances.


```python
with itab.query() as q:
    pprint.pprint(q.select())
```

    2023-11-07 15:57:55,420 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,421 INFO sqlalchemy.engine.Engine SELECT iris.id, iris.added, iris.petal_length, iris.petal_width, iris.sepal_length, iris.sepal_width, iris.species, iris.updated 
    FROM iris
    2023-11-07 15:57:55,422 INFO sqlalchemy.engine.Engine [cached since 0.08979s ago] ()
    [Iris(sepal_length=1.0,
          sepal_width=2.0,
          petal_length=3.0,
          petal_width=4.0,
          species='setosa',
          id=1,
          updated=datetime.datetime(2023, 11, 7, 20, 57, 55, 324955),
          added=datetime.datetime(2023, 11, 7, 20, 57, 55, 324953)),
     Iris(sepal_length=1.0,
          sepal_width=2.0,
          petal_length=3.0,
          petal_width=4.0,
          species='setosa',
          id=2,
          updated=datetime.datetime(2023, 11, 7, 20, 57, 55, 328715),
          added=datetime.datetime(2023, 11, 7, 20, 57, 55, 328713)),
     Iris(sepal_length=1.0,
          sepal_width=2.0,
          petal_length=3.0,
          petal_width=4.0,
          species='setosa',
          id=3,
          updated=datetime.datetime(2023, 11, 7, 20, 57, 55, 328720),
          added=datetime.datetime(2023, 11, 7, 20, 57, 55, 328719))]
    2023-11-07 15:57:55,423 INFO sqlalchemy.engine.Engine COMMIT


All of the same query types can be used.


```python
with itab.query() as q:
    q.delete(all=True)
    
    q.insert_multi(irises)
    
    db_irises = q.select()
    print(len(db_irises))
    pprint.pprint(db_irises[:2])
```

    2023-11-07 15:57:55,471 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,473 INFO sqlalchemy.engine.Engine DELETE FROM iris
    2023-11-07 15:57:55,474 INFO sqlalchemy.engine.Engine [cached since 0.1547s ago] ()
    2023-11-07 15:57:55,486 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO iris (added, petal_length, petal_width, sepal_length, sepal_width, species, updated) VALUES (?, ?, ?, ?, ?, ?, ?)
    2023-11-07 15:57:55,487 INFO sqlalchemy.engine.Engine [cached since 0.159s ago] [('2023-11-07 20:57:55.484095', 1.4, 0.2, 5.1, 3.5, 'setosa', '2023-11-07 20:57:55.484099'), ('2023-11-07 20:57:55.484100', 1.4, 0.2, 4.9, 3.0, 'setosa', '2023-11-07 20:57:55.484101'), ('2023-11-07 20:57:55.484101', 1.3, 0.2, 4.7, 3.2, 'setosa', '2023-11-07 20:57:55.484102'), ('2023-11-07 20:57:55.484103', 1.5, 0.2, 4.6, 3.1, 'setosa', '2023-11-07 20:57:55.484103'), ('2023-11-07 20:57:55.484104', 1.4, 0.2, 5.0, 3.6, 'setosa', '2023-11-07 20:57:55.484104'), ('2023-11-07 20:57:55.484105', 1.7, 0.4, 5.4, 3.9, 'setosa', '2023-11-07 20:57:55.484106'), ('2023-11-07 20:57:55.484106', 1.4, 0.3, 4.6, 3.4, 'setosa', '2023-11-07 20:57:55.484107'), ('2023-11-07 20:57:55.484108', 1.5, 0.2, 5.0, 3.4, 'setosa', '2023-11-07 20:57:55.484108')  ... displaying 10 of 150 total bound parameter sets ...  ('2023-11-07 20:57:55.484270', 5.4, 2.3, 6.2, 3.4, 'virginica', '2023-11-07 20:57:55.484270'), ('2023-11-07 20:57:55.484271', 5.1, 1.8, 5.9, 3.0, 'virginica', '2023-11-07 20:57:55.484271')]
    2023-11-07 15:57:55,489 INFO sqlalchemy.engine.Engine SELECT iris.id, iris.added, iris.petal_length, iris.petal_width, iris.sepal_length, iris.sepal_width, iris.species, iris.updated 
    FROM iris
    2023-11-07 15:57:55,490 INFO sqlalchemy.engine.Engine [cached since 0.1582s ago] ()
    150
    [Iris(sepal_length=5.1,
          sepal_width=3.5,
          petal_length=1.4,
          petal_width=0.2,
          species='setosa',
          id=1,
          updated=datetime.datetime(2023, 11, 7, 20, 57, 55, 484099),
          added=datetime.datetime(2023, 11, 7, 20, 57, 55, 484095)),
     Iris(sepal_length=4.9,
          sepal_width=3.0,
          petal_length=1.4,
          petal_width=0.2,
          species='setosa',
          id=2,
          updated=datetime.datetime(2023, 11, 7, 20, 57, 55, 484101),
          added=datetime.datetime(2023, 11, 7, 20, 57, 55, 484100))]
    2023-11-07 15:57:55,494 INFO sqlalchemy.engine.Engine COMMIT


Attributes that were not requested from the database reference the `doctable.MISSING` sentinel value.


```python
with itab.query() as q:
    db_irises = q.select(['id', 'sepal_width', 'sepal_length'])
    pprint.pprint(db_irises[:2])
```

    2023-11-07 15:57:55,524 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,526 INFO sqlalchemy.engine.Engine SELECT iris.id, iris.sepal_width, iris.sepal_length 
    FROM iris
    2023-11-07 15:57:55,527 INFO sqlalchemy.engine.Engine [generated in 0.00249s] ()
    [Iris(sepal_length=5.1,
          sepal_width=3.5,
          petal_length=MISSING,
          petal_width=MISSING,
          species=MISSING,
          id=1,
          updated=MISSING,
          added=MISSING),
     Iris(sepal_length=4.9,
          sepal_width=3.0,
          petal_length=MISSING,
          petal_width=MISSING,
          species=MISSING,
          id=2,
          updated=MISSING,
          added=MISSING)]
    2023-11-07 15:57:55,530 INFO sqlalchemy.engine.Engine COMMIT


## Working with Multple Tables

Now I'll demonstrate how to create and work with multi-table schemas with foreign key relationships.


```python
print(iris_df['species'].unique())

species_data = {
    'setosa':'bristle-pointed iris',
    'versicolor':'Southern blue flag',
    'virginica':'Northern blue flag',
}
```

    ['setosa' 'versicolor' 'virginica']


Here we create a foreign key constraint on the iris entries table that references a new species table.


```python
import typing

@doctable.table_schema(table_name='species')
class Species:
    name: str = doctable.Column(doctable.ColumnArgs(unique=True))
    common_name: str = doctable.Column(
        column_args=doctable.ColumnArgs(nullable=True),
    )
    id: int = doctable.Column(# will appear as the first column in the table
        column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
    )
    
    @classmethod
    def from_dict(cls, data: typing.Dict[str, str]) -> typing.List[Species]:
        return [cls(name=n, common_name=cn) for n,cn in data.items()]

@doctable.table_schema(
    table_name='iris_entry',
    constraints=[
        doctable.ForeignKey(['species'], ['species.name'], ondelete='CASCADE', onupdate='CASCADE'),
    ],
)
class IrisEntry:
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float
    species: str = doctable.Column(
        # NOTE: here I could add foreign_key='species.name' instead of adding fk constraint
        column_args=doctable.ColumnArgs(nullable=False),
    )
    
    id: int = doctable.Column(# will appear as the first column in the table
        column_args=doctable.ColumnArgs(order=0, primary_key=True, autoincrement=True),
    )
    
    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> typing.List[IrisEntry]:
        return [cls(**row) for _,row in df.iterrows()]


core = doctable.ConnectCore.open(
    target=':memory:', # use a filename for a sqlite to write to disk
    dialect='sqlite',
    echo=True,
)

with core.begin_ddl() as emitter:
    core.enable_foreign_keys()
    spec_tab = emitter.create_table_if_not_exists(Species)
    iris_tab = emitter.create_table_if_not_exists(IrisEntry)
print(spec_tab.inspect_columns())
```

    2023-11-07 15:57:55,647 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,648 INFO sqlalchemy.engine.Engine pragma foreign_keys=ON
    2023-11-07 15:57:55,649 INFO sqlalchemy.engine.Engine [generated in 0.00072s] ()
    2023-11-07 15:57:55,650 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-07 15:57:55,653 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,653 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("species")
    2023-11-07 15:57:55,654 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 15:57:55,656 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("species")
    2023-11-07 15:57:55,656 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 15:57:55,657 INFO sqlalchemy.engine.Engine PRAGMA main.table_info("iris_entry")
    2023-11-07 15:57:55,658 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 15:57:55,659 INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("iris_entry")
    2023-11-07 15:57:55,659 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 15:57:55,660 INFO sqlalchemy.engine.Engine 
    CREATE TABLE species (
    	id INTEGER, 
    	common_name VARCHAR, 
    	name VARCHAR, 
    	PRIMARY KEY (id), 
    	UNIQUE (name)
    )
    
    
    2023-11-07 15:57:55,661 INFO sqlalchemy.engine.Engine [no key 0.00057s] ()
    2023-11-07 15:57:55,664 INFO sqlalchemy.engine.Engine 
    CREATE TABLE iris_entry (
    	id INTEGER, 
    	petal_length FLOAT, 
    	petal_width FLOAT, 
    	sepal_length FLOAT, 
    	sepal_width FLOAT, 
    	species VARCHAR NOT NULL, 
    	PRIMARY KEY (id), 
    	FOREIGN KEY(species) REFERENCES species (name) ON DELETE CASCADE ON UPDATE CASCADE
    )
    
    
    2023-11-07 15:57:55,664 INFO sqlalchemy.engine.Engine [no key 0.00054s] ()
    2023-11-07 15:57:55,665 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-07 15:57:55,666 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,667 INFO sqlalchemy.engine.Engine PRAGMA main.table_xinfo("species")
    2023-11-07 15:57:55,668 INFO sqlalchemy.engine.Engine [raw sql] ()
    2023-11-07 15:57:55,668 INFO sqlalchemy.engine.Engine ROLLBACK
    [{'name': 'id', 'type': INTEGER(), 'nullable': True, 'default': None, 'primary_key': 1}, {'name': 'common_name', 'type': VARCHAR(), 'nullable': True, 'default': None, 'primary_key': 0}, {'name': 'name', 'type': VARCHAR(), 'nullable': True, 'default': None, 'primary_key': 0}]


Start by populating the species table.


```python
with spec_tab.query() as q:
    q.insert_multi(Species.from_dict(species_data), ifnotunique='replace')
    pprint.pprint(q.select())
```

    2023-11-07 15:57:55,766 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,767 INFO sqlalchemy.engine.Engine INSERT OR REPLACE INTO species (common_name, name) VALUES (?, ?)
    2023-11-07 15:57:55,768 INFO sqlalchemy.engine.Engine [generated in 0.00240s] [('bristle-pointed iris', 'setosa'), ('Southern blue flag', 'versicolor'), ('Northern blue flag', 'virginica')]
    2023-11-07 15:57:55,770 INFO sqlalchemy.engine.Engine SELECT species.id, species.common_name, species.name 
    FROM species
    2023-11-07 15:57:55,771 INFO sqlalchemy.engine.Engine [generated in 0.00073s] ()
    [Species(name='setosa', common_name='bristle-pointed iris', id=1),
     Species(name='versicolor', common_name='Southern blue flag', id=2),
     Species(name='virginica', common_name='Northern blue flag', id=3)]
    2023-11-07 15:57:55,772 INFO sqlalchemy.engine.Engine COMMIT


We will get an error if the provided species does not correspond to a row in the species table.


```python
try:
    with iris_tab.query() as q:
        q.insert_single(IrisEntry(
            sepal_length=1, 
            sepal_width=2, 
            petal_length=3, 
            petal_width=4, 
            species='wrongname' # THIS PART CAUSED THE ERROR!
        ))
except sqlalchemy.exc.IntegrityError:
    print('The species_name column is a foreign key to the species table, so it must be a valid species name.')
```

    2023-11-07 15:57:55,821 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,823 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO iris_entry (petal_length, petal_width, sepal_length, sepal_width, species) VALUES (?, ?, ?, ?, ?)
    2023-11-07 15:57:55,823 INFO sqlalchemy.engine.Engine [generated in 0.00239s] (3.0, 4.0, 1.0, 2.0, 'wrongname')
    2023-11-07 15:57:55,824 INFO sqlalchemy.engine.Engine COMMIT
    The species_name column is a foreign key to the species table, so it must be a valid species name.


Now that the species table is populated, we can insert the iris data.


```python
with iris_tab.query() as q:
    q.insert_multi(IrisEntry.from_dataframe(iris_df))
    print(q.select(limit=2))
```

    2023-11-07 15:57:55,939 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:57:55,940 INFO sqlalchemy.engine.Engine INSERT OR FAIL INTO iris_entry (petal_length, petal_width, sepal_length, sepal_width, species) VALUES (?, ?, ?, ?, ?)
    2023-11-07 15:57:55,941 INFO sqlalchemy.engine.Engine [generated in 0.00323s] [(1.4, 0.2, 5.1, 3.5, 'setosa'), (1.4, 0.2, 4.9, 3.0, 'setosa'), (1.3, 0.2, 4.7, 3.2, 'setosa'), (1.5, 0.2, 4.6, 3.1, 'setosa'), (1.4, 0.2, 5.0, 3.6, 'setosa'), (1.7, 0.4, 5.4, 3.9, 'setosa'), (1.4, 0.3, 4.6, 3.4, 'setosa'), (1.5, 0.2, 5.0, 3.4, 'setosa')  ... displaying 10 of 150 total bound parameter sets ...  (5.4, 2.3, 6.2, 3.4, 'virginica'), (5.1, 1.8, 5.9, 3.0, 'virginica')]
    2023-11-07 15:57:55,944 INFO sqlalchemy.engine.Engine SELECT iris_entry.id, iris_entry.petal_length, iris_entry.petal_width, iris_entry.sepal_length, iris_entry.sepal_width, iris_entry.species 
    FROM iris_entry
     LIMIT ? OFFSET ?
    2023-11-07 15:57:55,944 INFO sqlalchemy.engine.Engine [generated in 0.00088s] (2, 0)
    [IrisEntry(sepal_length=5.1, sepal_width=3.5, petal_length=1.4, petal_width=0.2, species='setosa', id=1), IrisEntry(sepal_length=4.9, sepal_width=3.0, petal_length=1.4, petal_width=0.2, species='setosa', id=2)]
    2023-11-07 15:57:55,945 INFO sqlalchemy.engine.Engine COMMIT


When the entry is deleted from the species tab, all associated irises are deleted.


```python
with spec_tab.query() as q:
    q.delete(spec_tab['name']=='setosa')
    print(f'{len(q.select())=}')

with core.query() as q:
    print(q.select([iris_tab['species'].distinct()]).fetchall())
```

    2023-11-07 15:59:34,029 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:59:34,031 INFO sqlalchemy.engine.Engine DELETE FROM species WHERE species.name = ?
    2023-11-07 15:59:34,031 INFO sqlalchemy.engine.Engine [cached since 98.05s ago] ('setosa',)
    2023-11-07 15:59:34,032 INFO sqlalchemy.engine.Engine SELECT species.id, species.common_name, species.name 
    FROM species
    2023-11-07 15:59:34,033 INFO sqlalchemy.engine.Engine [cached since 98.26s ago] ()
    len(q.select())=2
    2023-11-07 15:59:34,034 INFO sqlalchemy.engine.Engine COMMIT
    2023-11-07 15:59:34,035 INFO sqlalchemy.engine.Engine BEGIN (implicit)
    2023-11-07 15:59:34,036 INFO sqlalchemy.engine.Engine SELECT distinct(iris_entry.species) AS distinct_1 
    FROM iris_entry
    2023-11-07 15:59:34,037 INFO sqlalchemy.engine.Engine [cached since 98.05s ago] ()
    [('versicolor',), ('virginica',)]
    2023-11-07 15:59:34,038 INFO sqlalchemy.engine.Engine COMMIT

