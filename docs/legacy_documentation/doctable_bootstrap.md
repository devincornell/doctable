# Document Bootstrapping Examples
When estimating machine learning or statistical models on your corpus, you may need to bootstrap documents (randomly sample with replacement). The `.bootstrap()` method of `DocTable` will act like a select statement but return a bootstrap object instead of a direct query result. Here I show how to do some basic bootstrapping using an example doctable.


```python
import random
import pandas as pd
import numpy as np
import sys
sys.path.append('..')
import doctable as dt
```

### Create Example DocTable
First we define a DocTable that will be used for examples.


```python
schema = (
    ('integer','id',dict(primary_key=True, autoincrement=True)),
    ('string','name', dict(nullable=False, unique=True)),
    ('integer','age'),
    ('boolean', 'is_old'),
)
db = dt.DocTable(target=':memory:', schema=schema)
print(db)
```

    <DocTable::sqlite:///:memory::_documents_ ct: 0>


Then we add several example rows to the doctable.


```python
for i in range(10):
    age = random.random() # number in [0,1]
    is_old = age > 0.5
    row = {'name':'user_'+str(i), 'age':age, 'is_old':is_old}
    db.insert(row, ifnotunique='replace')

for doc in db.select(limit=3):
    print(doc)
```

    (1, 'user_0', 0.16086747483303065, False)
    (2, 'user_1', 0.14322051505126332, False)
    (3, 'user_2', 0.22664393988892395, False)


### Create a Bootstrap
We can use the doctable method `.bootstrap()` to return a bootstrap object using the keyword argument `n` to set the sample size (will use number of docs by default). This method acts like a select query, so we can specify columns and use the where argument to choose columns and rows to be bootstrapped. The bootsrap object contains the rows in the `.doc` property.

Notice that while our select statement drew three documens, the sample size specified with `n` is 5. The boostrap object will always return 5 objects, even though the number of docs stays the same.


```python
bs = db.bootstrap(['name','age'], where=db['id'] % 3 == 0, n=4)
print(type(bs))
print(len(bs.docs))
bs.n
```

    <class 'doctable.bootstrap.DocBootstrap'>
    3





    4



Use the bootstrap object as an iterator to access the bootstrapped docs. The bootstrap object draws a sample upon instantiation, so the same sample is maintained until reset.


```python
print('first run:')
for doc in bs:
    print(doc)
print('second run:')
for doc in bs:
    print(doc)
```

    first run:
    ('user_5', 0.6473182290263347)
    ('user_2', 0.22664393988892395)
    ('user_2', 0.22664393988892395)
    ('user_5', 0.6473182290263347)
    second run:
    ('user_5', 0.6473182290263347)
    ('user_2', 0.22664393988892395)
    ('user_2', 0.22664393988892395)
    ('user_5', 0.6473182290263347)


### Draw New Sample
You can reset the internal sample of the bootstrap object using the `.set_new_sample()` method. See that we now sample 2 docs and the output is different from previous runs. The sample will still remain the same each time we iterate until we reset the sample.


```python
bs.set_new_sample(2)
print('first run:')
for doc in bs:
    print(doc)
print('second run:')
for doc in bs:
    print(doc)
```

    first run:
    ('user_5', 0.6473182290263347)
    ('user_8', 0.5270190808172914)
    second run:
    ('user_5', 0.6473182290263347)
    ('user_8', 0.5270190808172914)


And we can iterate through a new sample using `.new_sample()`. Equivalent to calling `.set_new_sample()` and then iterating through elements.


```python
print('drawing new sample:')
for doc in bs.new_sample(3):
    print(doc)
print('repeating sample:')
for doc in bs:
    print(doc)
```

    drawing new sample:
    ('user_5', 0.6473182290263347)
    ('user_5', 0.6473182290263347)
    ('user_8', 0.5270190808172914)
    repeating sample:
    ('user_5', 0.6473182290263347)
    ('user_5', 0.6473182290263347)
    ('user_8', 0.5270190808172914)


I may add additional functionality in the future if I use this in any projects, but that's it for now.
