

```python
import random
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
import doctable as dt
```


```python
schema = (
    ('id','integer',dict(primary_key=True, autoincrement=True)),
    ('name','string', dict(nullable=False)),
    ('age','integer'),
    ('is_old', 'boolean'),
)
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
db = dt.DocTable2(schema, verbose=True)
for row in make_rows():
    db.insert(row)
db.select_df(verbose=False)
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
      <td>0.150690</td>
      <td>False</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>0.180140</td>
      <td>False</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>user_2</td>
      <td>0.642784</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python
db = dt.DocTable2(schema, verbose=True)
db.insert(list(make_rows()))
db.select_df(verbose=False)
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
      <td>0.519751</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>0.048514</td>
      <td>False</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>user_2</td>
      <td>0.875334</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Deletes


```python
# delete everything
db = dt.DocTable2(schema, verbose=True)
db.insert(list(make_rows()))
db.delete()
db.select_df(verbose=False)
```

    DocTable2 Query: DELETE FROM _documents_





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
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>




```python
# delete all entries where is_old is false
db = dt.DocTable2(schema, verbose=True)
db.insert(list(make_rows()))
db.delete(where=~db['is_old'])
db.select_df(verbose=False)
```

    DocTable2 Query: DELETE FROM _documents_ WHERE NOT _documents_.is_old





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
      <td>0.980449</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>0.805837</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python
# use vacuum to free unused space now
db = dt.DocTable2(schema, verbose=True)
db.insert(list(make_rows()))
db.delete(where=~db['is_old'], vacuum=True)
db.select_df(verbose=False)
```

    DocTable2 Query: DELETE FROM _documents_ WHERE NOT _documents_.is_old
    DocTable2 Query: VACUUM





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
      <td>2</td>
      <td>user_1</td>
      <td>0.917798</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>3</td>
      <td>user_2</td>
      <td>0.539498</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>


