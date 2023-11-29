# DocTable Examples: Insert and Delete
Here we show basics of inserting and deleting data into a doctable.


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
```


```python
def make_rows(N=3):
    rows = list()
    for i in range(N):
        age = random.random() # number in [0,1]
        is_old = age > 0.5
        yield {'name':'user_'+str(i), 'age':age, 'is_old':is_old}
    return rows
```

# Basic Inserts
There are only two ways to insert: one at a time (pass single dict), or multiple at a time (pass sequence of dicts).


```python
table = doctable.DocTable(target=':memory:', schema=Record, verbose=True)
for row in make_rows():
    table.insert(row)
table.select_df()
```

    DocTable: INSERT OR FAIL INTO _documents_ (name, age, is_old) VALUES (?, ?, ?)
    DocTable: INSERT OR FAIL INTO _documents_ (name, age, is_old) VALUES (?, ?, ?)
    DocTable: INSERT OR FAIL INTO _documents_ (name, age, is_old) VALUES (?, ?, ?)
    DocTable: SELECT _documents_.id, _documents_.name, _documents_.age, _documents_.is_old 
    FROM _documents_





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
      <td>0.485860</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1</td>
      <td>0.661900</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>user_2</td>
      <td>0.082627</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>




```python
newrows = list(make_rows())
table.insert(newrows)
table.select_df(verbose=False)
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
      <th>0</th>
      <td>1</td>
      <td>user_0</td>
      <td>0.485860</td>
      <td>False</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>user_1</td>
      <td>0.661900</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>user_2</td>
      <td>0.082627</td>
      <td>False</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>user_0</td>
      <td>0.936185</td>
      <td>True</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>user_1</td>
      <td>0.082005</td>
      <td>False</td>
    </tr>
    <tr>
      <th>5</th>
      <td>6</td>
      <td>user_2</td>
      <td>0.567260</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Deletes


```python
# delete all entries where is_old is false
table.delete(where=~table['is_old'])
table.select_df(verbose=False)
```

    DocTable: DELETE FROM _documents_ WHERE _documents_.is_old = 0





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
      <td>2</td>
      <td>user_1</td>
      <td>0.661900</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4</td>
      <td>user_0</td>
      <td>0.936185</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>6</td>
      <td>user_2</td>
      <td>0.567260</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python
# use vacuum to free unused space now
table.delete(where=~table['is_old'], vacuum=True)
table.select_df(verbose=False)
```

    DocTable: DELETE FROM _documents_ WHERE _documents_.is_old = 0
    DocTable: VACUUM





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
      <td>2</td>
      <td>user_1</td>
      <td>0.661900</td>
      <td>True</td>
    </tr>
    <tr>
      <th>1</th>
      <td>4</td>
      <td>user_0</td>
      <td>0.936185</td>
      <td>True</td>
    </tr>
    <tr>
      <th>2</th>
      <td>6</td>
      <td>user_2</td>
      <td>0.567260</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python
# delete everything
table.delete()
table.count()
```

    DocTable: DELETE FROM _documents_
    DocTable: SELECT count() AS count_1 
    FROM _documents_
     LIMIT ? OFFSET ?





    0


