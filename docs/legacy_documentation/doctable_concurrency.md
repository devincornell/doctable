# Concurrent Database Connections
DocTable makes it easy to establish concurrent database connections from different processes. DocTable objects can be copied as-is from one process to another, except that you must call `.reopen_engine()` to initialize in process thread. This removes now stale database connections (which are _not_ meant to traverse processes) from the engine connection pool.

You may also want to use a large timeout using the timeout argument of the doctable constructor (provided in seconds).


```python
import sqlalchemy
from multiprocessing import Process
import os
import random
import string
import dataclasses
import time
import sys
import pathlib
sys.path.append('..')
import doctable
```


```python
import datetime
@doctable.schema
class SimpleRow:
    __slots__ = []
    id: int = doctable.IDCol()
    updated: datetime.datetime = doctable.AddedCol()
    process: str = doctable.Col()
    number: int = doctable.Col()

#tmp = doctable.TempFolder('exdb')
import tempfile
tmpf = tempfile.TemporaryDirectory()
tmp = pathlib.Path(tmpf.name)
db = doctable.DocTable(schema=SimpleRow, target=tmp.joinpath('tmp_concurrent.db'), new_db=True, connect_args={'timeout': 15})
```


```python
def thread_func(numbers, db):
    process_id = ''.join(random.choices(string.ascii_uppercase, k=2))
    print(f'starting process {process_id}')
    db.reopen_engine() # create all new connections
    for num in numbers:
        db.insert({'process': process_id, 'number': num})
        time.sleep(0.01)

numbers = list(range(100)) # these numbers are to be inserted into the database
        
db.delete()
with doctable.Distribute(5) as d:
    d.map_chunk(thread_func, numbers, db)
db.head(10)
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:506: UserWarning: Method .delete() is depricated. Please use .q.delete() instead.
      warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')


    starting process OC
    starting process BI

    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '


    
    


    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '


    starting process FF

    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '


    starting process PC


    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '


    starting process YC

    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '


    


    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:408: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
      warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')





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
      <th>10</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>10</td>
    </tr>
  </tbody>
</table>
</div>


