# Concurrency
Databases are able to handle concurrency easily. The best way to use concurrent connections is to set the timeout parameter passed to the sqlalchemy.engine function as an extra argument to the constructure (captured by `**engine_args`). Note that while the ``persistent_conn`` constructor argument may have other uses, it does not have much of an effect on concurrent operations in this version of DocTable2.

Here I'll set up a simple test case for concurrent operations, where I run two threads simultaneously inserting many large data rows. We will see that when timeouts are set to be large, the threads take turns in inserting data.


```python
import sqlalchemy
from multiprocessing import Process
import os
import sys
sys.path.append('..')
import doctable as dt
```


```python
# define database schema to be sent to processes
fname = 'tmp_connections2.db'
schema = (
    ('id', 'integer', dict(primary_key=True, autoincrement=True)),
    ('data','pickle'),
    ('procname','string')
)
big_data = [i for i in range(10000000)] # create big data object
```


```python
# define a thread that takes a schema and inserts three big rows
def thread_writer(timeout, schema, fname, data, procname):
    db = dt.DocTable2(schema, persistent_conn=True, fname=fname, connect_args={'timeout': timeout})
    for i in range(3):
        try:
            db.insert({'data':data,'procname':procname})
        except sqlalchemy.exc.OperationalError:
            print('Raised the "(sqlite3.OperationalError) database is locked')
```


```python
# function to run the processes defined by thread_writer
def run_processes(timeout_sec, schema, fname, big_data):
    
    if os.path.exists(fname):
        os.remove(fname)
    
    baseargs = (timeout_sec,schema,fname,big_data)
    p1 = Process(target=thread_writer, args=(*baseargs,'p1'))
    p2 = Process(target=thread_writer, args=(*baseargs,'p2'))
    
    p1.start(), p2.start() # start the processes
    p1.join(), p2.join() # wait for processes to finish
```

## Correct Example
First we show a correctly working version with a sufficiently large timeout. Each thread will attempt to insert three large pickled objects (big lists) into the database. Because the timeout is sufficiently long, the processes will take turns in inserting data. You can see that effect by looking at the select statement below. The two threads have two different names that they inserted in the database, "p1" and "p2". The rows alternate.


```python
timeout = 10 # seconds
run_processes(timeout, schema, fname, big_data)
```


```python
db = dt.DocTable2(fname=fname)
print(db)
db.select(['id','procname'])
```

    <DocTable2::_documents_ ct: 6>





    [(1, 'p1'), (2, 'p2'), (3, 'p1'), (4, 'p2'), (5, 'p1'), (6, 'p2')]



## Failure Example
We can induce a failure case by setting the timeout to 0. Because the threads are inserting large python objects, one thread does not finish writing before the other attempts to write. When the insertion fails, it will give the python exception `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) database is locked`.


```python
timeout = 0 # seconds
run_processes(timeout, schema, fname, big_data)
```

    Raised the "(sqlite3.OperationalError) database is locked


Because the exception was caught, the threads continued to run. The results of an error means it will simply skip the given insert, but the behavior is in general undefined in this case.


```python
db = dt.DocTable2(fname=fname)
print(db)
db.select(['id','procname'])
```

    <DocTable2::_documents_ ct: 5>





    [(1, 'p1'), (2, 'p2'), (3, 'p1'), (4, 'p2'), (5, 'p1')]


