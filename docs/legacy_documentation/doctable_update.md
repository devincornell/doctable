# DocTable Examples: Update
Here I show how to update data into a DocTable. In addition to providing updated values, DocTable also allows you to create map functions to transform existing data.


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
        
def new_db():
    table = doctable.DocTable(schema=Record, target=':memory:', verbose=True)
    N = 10
    for i in range(N):
        age = random.random() # number in [0,1]
        is_old = age > 0.5
        table.insert({'name':'user_'+str(i), 'age':age, 'is_old':is_old}, verbose=False)
    return table

table = new_db()
print(table)
```

    <DocTable (4 cols)::sqlite:///:memory::_documents_>


    /DataDrive/code/doctable/examples/../doctable/doctable.py:324: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:350: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '



```python
table.select_df(limit=3)
```

    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_
     LIMIT ? OFFSET ?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
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
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>user_0</td>
      <td>0.998030</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1</td>
      <td>0.210891</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>user_2</td>
      <td>0.431233</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>



## Single Update
Update multiple (or single) rows with same values.


```python
table = new_db()
table.select_df(where=table['is_old']==True, limit=3, verbose=False)
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:324: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:350: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
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
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>user_0</td>
      <td>0.670833</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1</td>
      <td>0.895172</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>5</td>
      <td>user_4</td>
      <td>0.688209</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python
table = new_db()
table.update({'age':1},where=table['is_old']==True)
table.update({'age':0},where=table['is_old']==False)
table.select_df(limit=3, verbose=False)
```

    DocTable: UPDATE _documents_ SET age=? WHERE _documents_.is_old = 1
    DocTable: UPDATE _documents_ SET age=? WHERE _documents_.is_old = 0


    /DataDrive/code/doctable/examples/../doctable/doctable.py:324: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:350: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:440: UserWarning: Method .update() is depricated. Please use .q.update() instead.
      warnings.warn('Method .update() is depricated. Please use .q.update() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
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
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>user_0</td>
      <td>1</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1</td>
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>user_2</td>
      <td>1</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Apply as Map Function
This feature allows you to update columns based on the values of old columns.


```python
table = new_db()
values = {table['name']:table['name']+'th', table['age']:table['age']+1, table['is_old']:True}
table.update(values)
table.select_df(limit=3, verbose=False)
```

    DocTable: UPDATE _documents_ SET name=(_documents_.name || ?), age=(_documents_.age + ?), is_old=?


    /DataDrive/code/doctable/examples/../doctable/doctable.py:324: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:350: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:440: UserWarning: Method .update() is depricated. Please use .q.update() instead.
      warnings.warn('Method .update() is depricated. Please use .q.update() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
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
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>user_0th</td>
      <td>1.566417</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1th</td>
      <td>1.434875</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>user_2th</td>
      <td>1.422777</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Apply as Set of Ordered Map Functions
This is useful for when the updating of one column might change the value of another, depending on the order in which it was applied.


```python
table = new_db()
values = [(table['name'],table['age']-1), (table['age'],table['age']+1),]
table.update(values)
table.select_df(limit=3, verbose=False)
```

    DocTable: UPDATE _documents_ SET name=(_documents_.age - ?), age=(_documents_.age + ?)


    /DataDrive/code/doctable/examples/../doctable/doctable.py:324: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:350: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:440: UserWarning: Method .update() is depricated. Please use .q.update() instead.
      warnings.warn('Method .update() is depricated. Please use .q.update() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
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
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>-0.823513491706054</td>
      <td>1.176487</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>-0.567734080088791</td>
      <td>1.432266</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>-0.838314843815808</td>
      <td>1.161685</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>



## Update Using SQL WHERE String


```python
table = new_db()
table.update({'age':1.00}, wherestr='is_old==true')
table.select_df(limit=5, verbose=False)
```

    DocTable: UPDATE _documents_ SET age=? WHERE is_old==true


    /DataDrive/code/doctable/examples/../doctable/doctable.py:324: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:350: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:440: UserWarning: Method .update() is depricated. Please use .q.update() instead.
      warnings.warn('Method .update() is depricated. Please use .q.update() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:379: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
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
      <th>is_old</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>user_0</td>
      <td>0.488699</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1</td>
      <td>0.391556</td>
      <td>False</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>user_2</td>
      <td>1.000000</td>
      <td>True</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>user_3</td>
      <td>0.472176</td>
      <td>False</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>user_4</td>
      <td>0.154501</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>


