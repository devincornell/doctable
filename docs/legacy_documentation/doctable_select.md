# DocTable Examples: Select
Here I show how to select data from a DocTable. We cover object-oriented conditional selects emulating the `WHERE` SQL clause, as well as some reduce functions.


```python
import random
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
import doctable
```


```python
import dataclasses
@doctable.schema
class Record:
    __slots__ = []
    id: int = doctable.IDCol()
    name: str = doctable.Col(nullable=False)
    age: int = None
    is_old: bool = None

table = doctable.DocTable(target=':memory:', schema=Record, verbose=True)
print(table)
```

    <DocTable (4 cols)::sqlite:///:memory::_documents_>



```python
N = 10
for i in range(N):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    table.insert({'name':'user_'+str(i), 'age':age, 'is_old':is_old}, verbose=False)
print(table)
```

    <DocTable (4 cols)::sqlite:///:memory::_documents_>


    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '


## Regular Selects
These functions all return lists of ResultProxy objects. As such, they can be accessed using numerical indices or keyword indices. For instance, if one select output row is ```row=(1, 'user_0')``` (after selecting "id" and "user"), it can be accessed such that ```row[0]==row['id']``` and ```row[1]==row['user']```.


```python
# the limit argument means the result will only return some rows.
# I'll use it for convenience in these examples.
# this selects all rows
table.select(limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:449: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
table.select(['id','name'], limit=1)
```

    DocTable: SELECT _documents_.id, _documents_.name 
    FROM _documents_
     LIMIT ? OFFSET ?





    [Record(id=1, name='user_0', age=None, is_old=None)]




```python
# can also select by accessing the column object (db['id']) itself
# this will be useful later with more complex queries
table.select([table['id'],table['name']], limit=1)
```

    DocTable: SELECT _documents_.id, _documents_.name 
    FROM _documents_
     LIMIT ? OFFSET ?





    [Record(id=1, name='user_0', age=None, is_old=None)]




```python
table.select_first()
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:427: UserWarning: Method .select_first() is depricated. Please use .q.select_first() instead.
      warnings.warn('Method .select_first() is depricated. Please use .q.select_first() instead.')





    Record(id=1, name='user_0', age=0.30111935823671676, is_old=False)




```python
table.select('name',limit=5)
```

    DocTable: SELECT _documents_.name 
    FROM _documents_
     LIMIT ? OFFSET ?





    ['user_0', 'user_1', 'user_2', 'user_3', 'user_4']




```python
table.select_first('age')
```

    DocTable: SELECT _documents_.age 
    FROM _documents_
     LIMIT ? OFFSET ?





    Record(age=0.30111935823671676, is_old=None)



## Conditional Selects


```python
table.select(where=table['id']==2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id = ?





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
table.select(where=table['id']<3)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id < ?





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
# mod operator works too
table.select(where=(table['id']%2)==0, limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id % ? = ?
     LIMIT ? OFFSET ?





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True)]




```python
# note parantheses to handle order of ops with overloaded bitwise ops
table.select(where= (table['id']>=2) & (table['id']<=4) & (table['name']!='user_2'))
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id >= ? AND _documents_.id <= ? AND _documents_.name != ?





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True)]




```python
table.select(where=table['name'].in_(('user_2','user_3')))
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.name IN (__[POSTCOMPILE_name_1])





    [Record(id=3, name='user_2', age=0.33272186856831554, is_old=False),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True)]




```python
table.select(where=table['id'].between(2,4))
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id BETWEEN ? AND ?





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True),
     Record(id=3, name='user_2', age=0.33272186856831554, is_old=False),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True)]




```python
# use of logical not operator "~"
table.select(where= ~(table['name'].in_(('user_2','user_3'))) & (table['id'] < 4))
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE (_documents_.name NOT IN (__[POSTCOMPILE_name_1])) AND _documents_.id < ?





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
# more verbose operators .and_, .or_, and .not_ are bound to the doctable package
table.select(where= doctable.f.or_(doctable.f.not_(table['id']==4)) & (table['id'] <= 2))
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id != ? AND _documents_.id <= ?





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
# now with simple computation
ages = table.select(table['age'])
mean_age = sum(ages)/len(ages)
table.select(table['name'], where=table['age']>mean_age, limit=2)
```

    DocTable: SELECT _documents_.age 
    FROM _documents_
    DocTable: SELECT _documents_.name 
    FROM _documents_ 
    WHERE _documents_.age > ?
     LIMIT ? OFFSET ?





    ['user_1', 'user_3']




```python
# apply .label() method to columns
dict(table.select_first([table['age'].label('myage'), table['name'].label('myname')], as_dataclass=False))
```

    DocTable: SELECT _documents_.age AS myage, _documents_.name AS myname 
    FROM _documents_
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:429: UserWarning: The "as_dataclass" parameter has been depricated: please set get_raw=True or select_raw to specify that you would like to retrieve a raw RowProxy pobject.
      warnings.warn(f'The "as_dataclass" parameter has been depricated: please set get_raw=True or '





    {'myage': 0.30111935823671676, 'myname': 'user_0'}



## Column Operators
I bind the .min, .max, .count, .sum, and .mode methods to the column objects. Additionally, I move the .count method to a separate DocTable2 method.


```python
# with labels now
dict(table.select_first([table['age'].sum().label('sum'), table['age'].count().label('ct')], as_dataclass=False))
```

    DocTable: SELECT sum(_documents_.age) AS sum, count(_documents_.age) AS ct 
    FROM _documents_
     LIMIT ? OFFSET ?





    {'sum': 4.99992719426638, 'ct': 10}




```python
table.select_first([table['age'].sum(), table['age'].count(), table['age']], as_dataclass=False)
```

    DocTable: SELECT sum(_documents_.age) AS sum_1, count(_documents_.age) AS count_1, _documents_.age 
    FROM _documents_
     LIMIT ? OFFSET ?





    (4.99992719426638, 10, 0.30111935823671676)



## ORDER BY, GROUP BY, LIMIT
These additional arguments have also been provided.


```python
# the limit is obvious - it has been used throughout these examples
table.select(limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_
     LIMIT ? OFFSET ?





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
table.select([table['is_old'], doctable.f.count()], groupby=table['is_old'])
```

    DocTable: SELECT _documents_.is_old, count(*) AS count_1 
    FROM _documents_ GROUP BY _documents_.is_old
    DocTable: SELECT _documents_.is_old, count(*) AS count_1 
    FROM _documents_ GROUP BY _documents_.is_old


    /DataDrive/code/doctable/examples/../doctable/doctable.py:464: UserWarning: Conversion from row to object failed according to the following error. Please use .q.select_raw() when requesting non-object formatted data such as counts or sums in the future. For now it is automatically converted. e=RowDataConversionFailed("Conversion from <class 'sqlalchemy.engine.row.LegacyRow'> to <class '__main__.Record'> failed.")
      warnings.warn(f'Conversion from row to object failed according to the following '





    [(False, 5), (True, 5)]




```python
# orderby clause
table.select(orderby=table['age'].desc(), limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ ORDER BY _documents_.age DESC
     LIMIT ? OFFSET ?





    [Record(id=4, name='user_3', age=0.9011039173289395, is_old=True),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
# compound orderby
table.select(orderby=(table['age'].desc(),table['is_old'].asc()), limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ ORDER BY _documents_.age DESC, _documents_.is_old ASC
     LIMIT ? OFFSET ?





    [Record(id=4, name='user_3', age=0.9011039173289395, is_old=True),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
f = doctable.f
cols = [table['is_old'], f.count().label('ct')]
table.q.select_raw(cols, groupby=table['is_old'], orderby=f.asc('ct'))
```

    DocTable: SELECT _documents_.is_old, count(*) AS ct 
    FROM _documents_ GROUP BY _documents_.is_old ORDER BY ct ASC





    [(False, 5), (True, 5)]




```python
# can also use column name directly
# can only use ascending and can use only one col
table.select(orderby='age', limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ ORDER BY _documents_.age
     LIMIT ? OFFSET ?





    [Record(id=7, name='user_6', age=0.04850236983248746, is_old=False),
     Record(id=6, name='user_5', age=0.300309388680601, is_old=False)]




```python
# groupby clause
# returns first row of each group without any aggregation functions
table.select(groupby=table['is_old'])
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ GROUP BY _documents_.is_old





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=2, name='user_1', age=0.7524872495613466, is_old=True)]




```python
# compound groupby (weird example bc name is unique - have only one cat var in this demo)
table.select(groupby=(table['is_old'],table['name']), limit=3)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ GROUP BY _documents_.is_old, _documents_.name
     LIMIT ? OFFSET ?





    [Record(id=1, name='user_0', age=0.30111935823671676, is_old=False),
     Record(id=3, name='user_2', age=0.33272186856831554, is_old=False),
     Record(id=6, name='user_5', age=0.300309388680601, is_old=False)]




```python
# groupby clause using max aggregation function
# gets match age for both old and young groups
table.select(table['age'].max(), groupby=table['is_old'])
```

    DocTable: SELECT max(_documents_.age) AS max_1 
    FROM _documents_ GROUP BY _documents_.is_old





    [0.46166274965800924, 0.9011039173289395]



## SQL String Commands and Additional Clauses
For cases where DocTable2 does not provide a convenient interface, you may submit raw SQL commands. These may be a bit more unwieldly, but they offer maximum flexibility. They may be used either as simply an addition to the WHERE or arbitrary end clauses, or accessed in totality.


```python
qstr = 'SELECT age,name FROM {} WHERE id=="{}"'.format(table.tabname, 1)
results = table.execute(qstr)
dict(list(results)[0])
```

    DocTable: SELECT age,name FROM _documents_ WHERE id=="1"





    {'age': 0.30111935823671676, 'name': 'user_0'}




```python
wherestr = 'is_old=="{}"'.format('1')
table.select(wherestr=wherestr, limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE (is_old=="1")
     LIMIT ? OFFSET ?





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True)]




```python
# combine whrstr with structured query where clause
wherestr = 'is_old=="{}"'.format('1')
table.select(where=table['id']<=5, wherestr=wherestr)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id <= ? AND (is_old=="1")





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True),
     Record(id=5, name='user_4', age=0.6092744222076869, is_old=True)]




```python
# combine whrstr with structured query where clause
wherestr = 'is_old=="{}"'.format('1')
table.select(where=table['id']<=5, wherestr=wherestr)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_ 
    WHERE _documents_.id <= ? AND (is_old=="1")





    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True),
     Record(id=4, name='user_3', age=0.9011039173289395, is_old=True),
     Record(id=5, name='user_4', age=0.6092744222076869, is_old=True)]



## Count Method and Get Next ID
```.count()``` is a convenience method. Mostly the same could be accomplished by ```db.select_first(db['id'].count())```, but this requires no reference to a specific column.

```.next_id()``` is especially useful if one hopes to enter the id (or any primary key column) into new rows manually. Especially useful because SQL engines don't provide new ids except when a single insert is performed.


```python
table.count()
```

    DocTable: SELECT count(_documents_.id) AS count_1 
    FROM _documents_
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')





    10




```python
table.count(table['age'] < 0.5)
```

    DocTable: SELECT count(_documents_.id) AS count_1 
    FROM _documents_ 
    WHERE _documents_.age < ?
     LIMIT ? OFFSET ?





    5



## Select as Pandas Series and DataFrame
These are especially useful when working with metadata because Pandas provides robust descriptive and plotting features than SQL alone. Good for generating sample information.


```python
# must provide only a single column
table.select_series(table['age']).head(2)
```

    DocTable: SELECT _documents_.age 
    FROM _documents_





    0    0.301119
    1    0.752487
    dtype: float64




```python
table.select_series(table['age']).quantile([0.025, 0.985])
```

    DocTable: SELECT _documents_.age 
    FROM _documents_





    0.025    0.105159
    0.985    0.881041
    dtype: float64




```python
table.select_df(['id','age']).head(2)
```

    DocTable: SELECT _documents_.id, _documents_.age 
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
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>0.301119</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>0.752487</td>
    </tr>
  </tbody>
</table>
</div>




```python
table.select_df('age').head(2)
```

    DocTable: SELECT _documents_.age 
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
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.301119</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.752487</td>
    </tr>
  </tbody>
</table>
</div>




```python
# must provide list of cols (even for one col)
table.select_df([table['id'],table['age']]).corr()
```

    DocTable: SELECT _documents_.id, _documents_.age 
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
      <th>age</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>id</th>
      <td>1.000000</td>
      <td>0.006293</td>
    </tr>
    <tr>
      <th>age</th>
      <td>0.006293</td>
      <td>1.000000</td>
    </tr>
  </tbody>
</table>
</div>




```python
table.select_df([table['id'],table['age']]).describe().T
```

    DocTable: SELECT _documents_.id, _documents_.age 
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
      <th>count</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>id</th>
      <td>10.0</td>
      <td>5.500000</td>
      <td>3.027650</td>
      <td>1.000000</td>
      <td>3.25000</td>
      <td>5.500000</td>
      <td>7.750000</td>
      <td>10.000000</td>
    </tr>
    <tr>
      <th>age</th>
      <td>10.0</td>
      <td>0.499993</td>
      <td>0.256825</td>
      <td>0.048502</td>
      <td>0.30902</td>
      <td>0.535469</td>
      <td>0.659958</td>
      <td>0.901104</td>
    </tr>
  </tbody>
</table>
</div>




```python
mean_age = table.select_series(table['age']).mean()
df = table.select_df([table['id'],table['age']])
df['old_grp'] = df['age'] > mean_age
df.groupby('old_grp').describe()
```

    DocTable: SELECT _documents_.age 
    FROM _documents_
    DocTable: SELECT _documents_.id, _documents_.age 
    FROM _documents_


    /DataDrive/code/doctable/examples/../doctable/doctable.py:415: UserWarning: Method .select_series() is depricated. Please use .q.select_series() instead.
      warnings.warn('Method .select_series() is depricated. Please use .q.select_series() instead.')
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

    .dataframe thead tr th {
        text-align: left;
    }

    .dataframe thead tr:last-of-type th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th colspan="8" halign="left">id</th>
      <th colspan="8" halign="left">age</th>
    </tr>
    <tr>
      <th></th>
      <th>count</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
      <th>count</th>
      <th>mean</th>
      <th>std</th>
      <th>min</th>
      <th>25%</th>
      <th>50%</th>
      <th>75%</th>
      <th>max</th>
    </tr>
    <tr>
      <th>old_grp</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>False</th>
      <td>5.0</td>
      <td>5.0</td>
      <td>2.915476</td>
      <td>1.0</td>
      <td>3.0</td>
      <td>6.0</td>
      <td>7.0</td>
      <td>8.0</td>
      <td>5.0</td>
      <td>0.288863</td>
      <td>0.149865</td>
      <td>0.048502</td>
      <td>0.300309</td>
      <td>0.301119</td>
      <td>0.332722</td>
      <td>0.461663</td>
    </tr>
    <tr>
      <th>True</th>
      <td>5.0</td>
      <td>6.0</td>
      <td>3.391165</td>
      <td>2.0</td>
      <td>4.0</td>
      <td>5.0</td>
      <td>9.0</td>
      <td>10.0</td>
      <td>5.0</td>
      <td>0.711122</td>
      <td>0.120456</td>
      <td>0.609274</td>
      <td>0.619203</td>
      <td>0.673543</td>
      <td>0.752487</td>
      <td>0.901104</td>
    </tr>
  </tbody>
</table>
</div>




```python
# more complicated groupby aggregation.
# calculates the variance both for entries above and below average age
mean_age = table.select_series(table['age']).mean()
df = table.select_df([table['name'],table['age']])
df['old_grp'] = df['age']>mean_age
df.groupby('old_grp').agg(**{
    'first_name':pd.NamedAgg(column='name', aggfunc='first'),
    'var_age':pd.NamedAgg(column='age', aggfunc=np.var),
})
```

    DocTable: SELECT _documents_.age 
    FROM _documents_
    DocTable: SELECT _documents_.name, _documents_.age 
    FROM _documents_


    /DataDrive/code/doctable/examples/../doctable/doctable.py:415: UserWarning: Method .select_series() is depricated. Please use .q.select_series() instead.
      warnings.warn('Method .select_series() is depricated. Please use .q.select_series() instead.')
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
      <th>first_name</th>
      <th>var_age</th>
    </tr>
    <tr>
      <th>old_grp</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>False</th>
      <td>user_0</td>
      <td>0.022459</td>
    </tr>
    <tr>
      <th>True</th>
      <td>user_1</td>
      <td>0.014510</td>
    </tr>
  </tbody>
</table>
</div>



# Select with Buffer
In cases where you have many rows or each row contains a lot of data, you may want to perform a select query which makes requests in chunks. This is performed using the SQL OFFSET command, and querying up to buffsize while yielding each returned row. This system is designed this way because the underlying sql engine buffers all rows retreived from a query, and thus there is no way to stream data into memory without this system.

NOTE: The limit keyword is incompatible with this method - it will return all results. A workaround is to use the approx_max_rows param, which will return at minimum this number of rows, at max the specified number of rows plus buffsize.


```python
for row_chunk in table.select_chunks(chunksize=2, where=(table['id']%2)==0, verbose=False):
    print(row_chunk)
```

    [Record(id=2, name='user_1', age=0.7524872495613466, is_old=True), Record(id=4, name='user_3', age=0.9011039173289395, is_old=True)]
    [Record(id=6, name='user_5', age=0.300309388680601, is_old=False), Record(id=8, name='user_7', age=0.46166274965800924, is_old=False)]
    [Record(id=10, name='user_9', age=0.6192026652607745, is_old=True)]
    []

