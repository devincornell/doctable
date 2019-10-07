

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
def new_db():
    db = dt.DocTable2(schema, tabname='mydocuments', verbose=True)
    N = 10
    for i in range(N):
        age = random.random() # number in [0,1]
        is_old = age > 0.5
        db.insert({'name':'user_'+str(i), 'age':age, 'is_old':is_old}, verbose=False)
    return db

db = new_db()
print(db)
```

    DocTable2 Query: SELECT count() AS count_1 
    FROM mydocuments
     LIMIT :param_1
    <DocTable2::mydocuments ct: 10>



```python
db.select_df(limit=3)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments
     LIMIT :param_1





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
      <td>0.342088</td>
      <td>False</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>0.958548</td>
      <td>True</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>user_2</td>
      <td>0.999047</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Single Update
Update multiple (or single) rows with same values.


```python
db = new_db()
db.select_df(where=db['is_old']==True, limit=3, verbose=False)
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
      <td>0.725059</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>5</td>
      <td>user_4</td>
      <td>0.697233</td>
      <td>True</td>
    </tr>
    <tr>
      <td>2</td>
      <td>9</td>
      <td>user_8</td>
      <td>0.515677</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>




```python
db = new_db()
db.update({'age':1},where=db['is_old']==True)
db.update({'age':0},where=db['is_old']==False)
db.select_df(limit=3, verbose=False)
```

    DocTable2 Query: UPDATE mydocuments SET age=:age WHERE mydocuments.is_old = true
    DocTable2 Query: UPDATE mydocuments SET age=:age WHERE mydocuments.is_old = false





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
      <td>0</td>
      <td>False</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>1</td>
      <td>True</td>
    </tr>
    <tr>
      <td>2</td>
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
db = new_db()
values = {db['name']:db['name']+'th', db['age']:db['age']+1, db['is_old']:True}
db.update(values)
db.select_df(limit=3, verbose=False)
```

    DocTable2 Query: UPDATE mydocuments SET name=(mydocuments.name || :name_1), age=(mydocuments.age + :age_1), is_old=:is_old





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
      <td>user_0th</td>
      <td>1.385227</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1th</td>
      <td>1.114447</td>
      <td>True</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>user_2th</td>
      <td>1.364155</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Apply as Set of Ordered Map Functions
This is useful for when the updating of one column might change the value of another, depending on the order in which it was applied.


```python
db = new_db()
values = [(db['name'],db['age']-1), (db['age'],db['age']+1),]
db.update(values)
db.select_df(limit=3, verbose=False)
```

    DocTable2 Query: UPDATE mydocuments SET name=(mydocuments.age - :age_1), age=(mydocuments.age + :age_2)





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
      <td>-0.0727614249612974</td>
      <td>1.927239</td>
      <td>True</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>-0.652814265979039</td>
      <td>1.347186</td>
      <td>False</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>-0.301096674435441</td>
      <td>1.698903</td>
      <td>True</td>
    </tr>
  </tbody>
</table>
</div>



## Update Using SQL WHERE String


```python
db = new_db()
db.update({'age':1.00},whrstr='is_old==true')
db.select_df(limit=5, verbose=False)
```

    DocTable2 Query: UPDATE mydocuments SET age=:age WHERE is_old==true





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
      <td>0.058850</td>
      <td>False</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>user_1</td>
      <td>1.000000</td>
      <td>True</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>user_2</td>
      <td>1.000000</td>
      <td>True</td>
    </tr>
    <tr>
      <td>3</td>
      <td>4</td>
      <td>user_3</td>
      <td>1.000000</td>
      <td>True</td>
    </tr>
    <tr>
      <td>4</td>
      <td>5</td>
      <td>user_4</td>
      <td>0.103194</td>
      <td>False</td>
    </tr>
  </tbody>
</table>
</div>


