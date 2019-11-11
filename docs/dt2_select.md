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
db = dt.DocTable2(schema, tabname='mydocuments', verbose=True)
# defaults: #fname=':memory:', engine='sqlite', persistent_conn=True, new_db=True
# fname=':memory:' is special - it loads database into memory
print(db)
```

    DocTable2 Query: SELECT count() AS count_1 
    FROM mydocuments
     LIMIT :param_1
    <DocTable2::mydocuments ct: 0>



```python
N = 10
for i in range(N):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    db.insert({'name':'user_'+str(i), 'age':age, 'is_old':is_old}, verbose=False)
print(db)
```

    DocTable2 Query: SELECT count() AS count_1 
    FROM mydocuments
     LIMIT :param_1
    <DocTable2::mydocuments ct: 10>


## Regular Selects
These functions all return lists of ResultProxy objects. As such, they can be accessed using numerical indices or keyword indices. For instance, if one select output row is ```row=(1, 'user_0')``` (after selecting "id" and "user"), it can be accessed such that ```row[0]==row['id']``` and ```row[1]==row['user']```.


```python
# the limit argument means the result will only return some rows.
# I'll use it for convenience in these examples.
# this selects all rows
db.select(limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments
     LIMIT :param_1





    [(1, 'user_0', 0.3164412298275918, False),
     (2, 'user_1', 0.16846270602459934, False)]




```python
db.select(['id','name'], limit=1)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name 
    FROM mydocuments
     LIMIT :param_1





    [(1, 'user_0')]




```python
# can also select by accessing the column object (db['id']) itself
# this will be useful later with more complex queries
db.select([db['id'],db['name']], limit=1)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name 
    FROM mydocuments
     LIMIT :param_1





    [(1, 'user_0')]




```python
db.select_first()
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments
     LIMIT :param_1





    (1, 'user_0', 0.3164412298275918, False)




```python
db.select('name',limit=5)
```

    DocTable2 Query: SELECT mydocuments.name 
    FROM mydocuments
     LIMIT :param_1





    ['user_0', 'user_1', 'user_2', 'user_3', 'user_4']




```python
db.select_first('age')
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments
     LIMIT :param_1





    0.3164412298275918



## Conditional Selects


```python
db.select(where=db['id']==2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id = :id_1





    [(2, 'user_1', 0.16846270602459934, False)]




```python
db.select(where=db['id']<3)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id < :id_1





    [(1, 'user_0', 0.3164412298275918, False),
     (2, 'user_1', 0.16846270602459934, False)]




```python
# mod operator works too
db.select(where=(db['id']%2)==0, limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id % :id_1 = :param_1
     LIMIT :param_2





    [(2, 'user_1', 0.16846270602459934, False),
     (4, 'user_3', 0.8760700109368977, True)]




```python
# note parantheses to handle order of ops with overloaded bitwise ops
db.select(where= (db['id']>=2) & (db['id']<=4) & (db['name']!='user_2'))
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id >= :id_1 AND mydocuments.id <= :id_2 AND mydocuments.name != :name_1





    [(2, 'user_1', 0.16846270602459934, False),
     (4, 'user_3', 0.8760700109368977, True)]




```python
db.select(where=db['name'].in_(('user_2','user_3')))
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.name IN (:name_1, :name_2)





    [(3, 'user_2', 0.5487944288357308, True),
     (4, 'user_3', 0.8760700109368977, True)]




```python
db.select(where=db['id'].between(2,4))
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id BETWEEN :id_1 AND :id_2





    [(2, 'user_1', 0.16846270602459934, False),
     (3, 'user_2', 0.5487944288357308, True),
     (4, 'user_3', 0.8760700109368977, True)]




```python
# use of logical not operator "~"
db.select(where= ~(db['name'].in_(('user_2','user_3'))) & (db['id'] < 4))
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.name NOT IN (:name_1, :name_2) AND mydocuments.id < :id_1





    [(1, 'user_0', 0.3164412298275918, False),
     (2, 'user_1', 0.16846270602459934, False)]




```python
# more verbose operators .and_, .or_, and .not_ are bound to the doctable package
db.select(where= dt.or_(dt.not_(db['id']==4)) & (db['id'] <= 2))
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id != :id_1 AND mydocuments.id <= :id_2





    [(1, 'user_0', 0.3164412298275918, False),
     (2, 'user_1', 0.16846270602459934, False)]




```python
# now with simple computation
ages = db.select(db['age'])
mean_age = sum(ages)/len(ages)
db.select(db['name'], where=db['age']>mean_age, limit=2)
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments
    DocTable2 Query: SELECT mydocuments.name 
    FROM mydocuments 
    WHERE mydocuments.age > :age_1
     LIMIT :param_1





    ['user_3', 'user_5']




```python
# apply .label() method to columns
dict(db.select_first([db['age'].label('myage'), db['name'].label('myname')]))
```

    DocTable2 Query: SELECT mydocuments.age AS myage, mydocuments.name AS myname 
    FROM mydocuments
     LIMIT :param_1





    {'myage': 0.3164412298275918, 'myname': 'user_0'}



## Column Operators
I bind the .min, .max, .count, .sum, and .mode methods to the column objects. Additionally, I move the .count method to a separate DocTable2 method.


```python
db.select_first([db['age'].sum, db['age'].count, db['age']])
```

    DocTable2 Query: SELECT sum(mydocuments.age) AS sum_1, count(mydocuments.age) AS count_1, mydocuments.age 
    FROM mydocuments
     LIMIT :param_1





    (5.5745842928905915, 10, 0.3164412298275918)




```python
# with labels now
dict(db.select_first([db['age'].sum.label('sum'), db['age'].count.label('ct')]))
```

    DocTable2 Query: SELECT sum(mydocuments.age) AS sum, count(mydocuments.age) AS ct 
    FROM mydocuments
     LIMIT :param_1





    {'sum': 5.5745842928905915, 'ct': 10}



## ORDER BY, GROUP BY, LIMIT
These additional arguments have also been provided.


```python
# the limit is obvious - it has been used throughout these examples
db.select(limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments
     LIMIT :param_1





    [(1, 'user_0', 0.3164412298275918, False),
     (2, 'user_1', 0.16846270602459934, False)]




```python
# orderby clause
db.select(orderby=db['age'].desc(), limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments ORDER BY mydocuments.age DESC
     LIMIT :param_1





    [(4, 'user_3', 0.8760700109368977, True),
     (9, 'user_8', 0.8706290541203731, True)]




```python
# compound orderby
db.select(orderby=(db['age'].desc(),db['is_old'].asc()), limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments ORDER BY mydocuments.age DESC, mydocuments.is_old ASC
     LIMIT :param_1





    [(4, 'user_3', 0.8760700109368977, True),
     (9, 'user_8', 0.8706290541203731, True)]




```python
# can also use column name directly
# can only use ascending and can use only one col
db.select(orderby='age', limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments ORDER BY mydocuments.age
     LIMIT :param_1





    [(5, 'user_4', 0.050003572489580095, False),
     (2, 'user_1', 0.16846270602459934, False)]




```python
# groupby clause
# returns first row of each group without any aggregation functions
db.select(groupby=db['is_old'])
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments GROUP BY mydocuments.is_old





    [(1, 'user_0', 0.3164412298275918, False),
     (3, 'user_2', 0.5487944288357308, True)]




```python
# compound groupby (weird example bc name is unique - have only one cat var in this demo)
db.select(groupby=(db['is_old'],db['name']), limit=3)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments GROUP BY mydocuments.is_old, mydocuments.name
     LIMIT :param_1





    [(1, 'user_0', 0.3164412298275918, False),
     (2, 'user_1', 0.16846270602459934, False),
     (5, 'user_4', 0.050003572489580095, False)]




```python
# groupby clause using max aggregation function
# gets match age for both old and young groups
db.select(db['age'].max, groupby=db['is_old'])
```

    DocTable2 Query: SELECT max(mydocuments.age) AS max_1 
    FROM mydocuments GROUP BY mydocuments.is_old





    [0.3164412298275918, 0.8760700109368977]



## SQL String Commands and Additional Clauses
For cases where DocTable2 does not provide a convenient interface, you may submit raw SQL commands. These may be a bit more unwieldly, but they offer maximum flexibility. They may be used either as simply an addition to the WHERE or arbitrary end clauses, or accessed in totality.


```python
qstr = 'SELECT age,name FROM {} WHERE id=="{}"'.format(db.tabname, 1)
results = db.execute(qstr)
dict(list(results)[0])
```

    DocTable2 Query: SELECT age,name FROM mydocuments WHERE id=="1"





    {'age': 0.3164412298275918, 'name': 'user_0'}




```python
whrstr = 'is_old=="{}"'.format('1')
db.select(whrstr=whrstr, limit=2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE is_old=="1"
     LIMIT :param_1





    [(3, 'user_2', 0.5487944288357308, True),
     (4, 'user_3', 0.8760700109368977, True)]




```python
# combine whrstr with structured query where clause
whrstr = 'is_old=="{}"'.format('1')
db.select(where=db['id']<=5, whrstr=whrstr)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id <= :id_1 AND is_old=="1"





    [(3, 'user_2', 0.5487944288357308, True),
     (4, 'user_3', 0.8760700109368977, True)]




```python
# combine whrstr with structured query where clause
whrstr = 'is_old=="{}"'.format('1')
db.select(where=db['id']<=5, whrstr=whrstr)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id <= :id_1 AND is_old=="1"





    [(3, 'user_2', 0.5487944288357308, True),
     (4, 'user_3', 0.8760700109368977, True)]



## Count Method and Get Next ID
```.count()``` is a convenience method. Mostly the same could be accomplished by ```db.select_first(db['id'].count)```, but this requires no reference to a specific column.

```.next_id()``` is especially useful if one hopes to enter the id (or any primary key column) into new rows manually. Especially useful because SQL engines don't provide new ids except when a single insert is performed.


```python
db.count()
```

    DocTable2 Query: SELECT count() AS count_1 
    FROM mydocuments
     LIMIT :param_1





    10




```python
db.count(db['age'] < 0.5)
```

    DocTable2 Query: SELECT count() AS count_1 
    FROM mydocuments 
    WHERE mydocuments.age < :age_1
     LIMIT :param_1





    3




```python
db.next_id()
```

    DocTable2 Query: SELECT max(mydocuments.id) AS max_1 
    FROM mydocuments
     LIMIT :param_1





    11




```python
# weird (but possible) with 'age' because it's not an actual primary key
db.next_id(idcol='age')
```

    DocTable2 Query: SELECT max(mydocuments.age) AS max_1 
    FROM mydocuments
     LIMIT :param_1





    1.8760700109368977



## Select as Pandas Series and DataFrame
These are especially useful when working with metadata because Pandas provides robust descriptive and plotting features than SQL alone. Good for generating sample information.


```python
# must provide only a single column
db.select_series(db['age']).head(2)
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments





    0    0.316441
    1    0.168463
    dtype: float64




```python
db.select_series(db['age']).quantile([0.025, 0.985])
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments





    0.025    0.076657
    0.985    0.875335
    dtype: float64




```python
db.select_df(['id','age']).head(2)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.age 
    FROM mydocuments





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
      <td>0</td>
      <td>1</td>
      <td>0.316441</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>0.168463</td>
    </tr>
  </tbody>
</table>
</div>




```python
db.select_df('age').head(2)
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments





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
      <td>0</td>
      <td>0.316441</td>
    </tr>
    <tr>
      <td>1</td>
      <td>0.168463</td>
    </tr>
  </tbody>
</table>
</div>




```python
# must provide list of cols (even for one col)
db.select_df([db['id'],db['age']]).corr()
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.age 
    FROM mydocuments





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
      <td>id</td>
      <td>1.000000</td>
      <td>0.579989</td>
    </tr>
    <tr>
      <td>age</td>
      <td>0.579989</td>
      <td>1.000000</td>
    </tr>
  </tbody>
</table>
</div>




```python
db.select_df([db['id'],db['age']]).describe().T
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.age 
    FROM mydocuments





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
      <td>id</td>
      <td>10.0</td>
      <td>5.500000</td>
      <td>3.02765</td>
      <td>1.000000</td>
      <td>3.25000</td>
      <td>5.500000</td>
      <td>7.750000</td>
      <td>10.00000</td>
    </tr>
    <tr>
      <td>age</td>
      <td>10.0</td>
      <td>0.557458</td>
      <td>0.28826</td>
      <td>0.050004</td>
      <td>0.37453</td>
      <td>0.625552</td>
      <td>0.748219</td>
      <td>0.87607</td>
    </tr>
  </tbody>
</table>
</div>




```python
mean_age = db.select_series(db['age']).mean()
df = db.select_df([db['id'],db['age']])
df['old_grp'] = df['age'] > mean_age
df.groupby('old_grp').describe()
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments
    DocTable2 Query: SELECT mydocuments.id, mydocuments.age 
    FROM mydocuments





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
      <td>False</td>
      <td>4.0</td>
      <td>2.750000</td>
      <td>1.707825</td>
      <td>1.0</td>
      <td>1.75</td>
      <td>2.5</td>
      <td>3.50</td>
      <td>5.0</td>
      <td>4.0</td>
      <td>0.270925</td>
      <td>0.214933</td>
      <td>0.050004</td>
      <td>0.138848</td>
      <td>0.242452</td>
      <td>0.374530</td>
      <td>0.548794</td>
    </tr>
    <tr>
      <td>True</td>
      <td>6.0</td>
      <td>7.333333</td>
      <td>2.160247</td>
      <td>4.0</td>
      <td>6.25</td>
      <td>7.5</td>
      <td>8.75</td>
      <td>10.0</td>
      <td>6.0</td>
      <td>0.748480</td>
      <td>0.111277</td>
      <td>0.610373</td>
      <td>0.666343</td>
      <td>0.746540</td>
      <td>0.840446</td>
      <td>0.876070</td>
    </tr>
  </tbody>
</table>
</div>




```python
# more complicated groupby aggregation.
# calculates the variance both for entries above and below average age
mean_age = db.select_series(db['age']).mean()
df = db.select_df([db['name'],db['age']])
df['old_grp'] = df['age']>mean_age
df.groupby('old_grp').agg(**{
    'first_name':pd.NamedAgg(column='name', aggfunc='first'),
    'var_age':pd.NamedAgg(column='age', aggfunc=np.var),
})
```

    DocTable2 Query: SELECT mydocuments.age 
    FROM mydocuments
    DocTable2 Query: SELECT mydocuments.name, mydocuments.age 
    FROM mydocuments





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
      <td>False</td>
      <td>user_0</td>
      <td>0.046196</td>
    </tr>
    <tr>
      <td>True</td>
      <td>user_3</td>
      <td>0.012383</td>
    </tr>
  </tbody>
</table>
</div>



# Select with Buffer
In cases where you have many rows or each row contains a lot of data, you may want to perform a select query which makes requests in chunks. This is performed using the SQL OFFSET command, and querying up to buffsize while yielding each returned row. This system is designed this way because the underlying sql engine buffers all rows retreived from a query, and thus there is no way to stream data into memory without this system.

NOTE: The limit keyword is incompatible with this method - it will return all results. A workaround is to use the approx_max_rows param, which will return at minimum this number of rows, at max the specified number of rows plus buffsize.


```python
for row in db.select_chunk(chunksize=2, max_rows=3, where=(db['id']%2)==0):
    print(row)
```

    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id % :id_1 = :param_1
     LIMIT :param_2 OFFSET :param_3
    (2, 'user_1', 0.16846270602459934, False)
    (4, 'user_3', 0.8760700109368977, True)
    DocTable2 Query: SELECT mydocuments.id, mydocuments.name, mydocuments.age, mydocuments.is_old 
    FROM mydocuments 
    WHERE mydocuments.id % :id_1 = :param_1
     LIMIT :param_2 OFFSET :param_3
    (6, 'user_5', 0.7431812816282332, True)


# Bootstrap Select
Often it is desirable to bootstrap select (sample with replacement) from a document sample. DocTable2 includes this feature.


```python
db.select_bootstrap(nsamp=10, verbose=False)
```

    DocTable2 Query: SELECT mydocuments.id 
    FROM mydocuments





    [(2, 'user_1', 0.16846270602459934, False),
     (3, 'user_2', 0.5487944288357308, True),
     (6, 'user_5', 0.7431812816282332, True),
     (7, 'user_6', 0.6407300749770457, True),
     (8, 'user_7', 0.6103732528229019, True),
     (9, 'user_8', 0.8706290541203731, True),
     (2, 'user_1', 0.16846270602459934, False),
     (3, 'user_2', 0.5487944288357308, True),
     (8, 'user_7', 0.6103732528229019, True),
     (2, 'user_1', 0.16846270602459934, False)]

