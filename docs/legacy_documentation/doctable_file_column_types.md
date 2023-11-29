# DocTable File Column Types
It is often good advice to avoid storing large binary data in an SQL table because it will significantly impact the read performance of the entire table. I find, however, that it can be extremely useful in text analysis applications as a way to keep track of a large number of models with associated metadata. As an alternative to storing binary data in the table directly, `DocTable` includes a number of custom column types that can transparently store data into the filesystem and keep track of it using the schema definitions.

I provide two file storage column types: (1) `TextFileCol` for storing text data, and (2) `PickleFileCol` for storing any python data that requires pickling.


```python
import numpy as np
from pathlib import Path

import sys
sys.path.append('..')
import doctable

# automatically clean up temp folder after python ends
import tempfile
tempdir = tempfile.TemporaryDirectory()
tmpfolder = tempdir.name
tmpfolder = Path(tmpfolder)
tmpfolder
```




    PosixPath('/tmp/tmpkoe57pma')



Now I create a new table representing a matrix. Notice that I use the `PickleFileCol` column shortcut to create the column. This column is equivalent to `Col(None, coltype='picklefile', type_args=dict(folder=folder))`. See that to SQLite, this column simply looks like a text column.


```python
import dataclasses
@doctable.schema(require_slots=False)
class MatrixRow:
    id: int = doctable.IDCol()
    array: np.ndarray = doctable.PickleFileCol(f'{tmpfolder}/matrix_pickle_files') # will store files in the tmp directory
    
db = doctable.DocTable(target=f'{tmpfolder}/test.db', schema=MatrixRow, new_db=True)
db.schema_info()
```




    [{'name': 'id',
      'type': INTEGER(),
      'nullable': False,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 1},
     {'name': 'array',
      'type': VARCHAR(),
      'nullable': True,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 0}]



Now we insert a new array. It appears to be inserted the same as any other object. 


```python
db.insert({'array': np.random.rand(10,10)})
db.insert({'array': np.random.rand(10,10)})
print(db.count())
db.select_df(limit=3)
```

    2


    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:420: UserWarning: Method .select_df() is depricated. Please use .q.select_df() instead.
      warnings.warn('Method .select_df() is depricated. Please use .q.select_df() instead.')
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: TypeDecorator PickleFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)





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
      <th>array</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>[[0.5329174823769329, 0.45399901667272, 0.4110...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>[[0.6837499182333924, 0.40540705856582326, 0.6...</td>
    </tr>
  </tbody>
</table>
</div>



But when we actually look at the filesystem, we see that files have been created to store the array.


```python
for fpath in tmpfolder.rglob('*.pic'):
    print(str(fpath))
```

    /tmp/tmpkoe57pma/matrix_pickle_files/838448859815.pic
    /tmp/tmpkoe57pma/matrix_pickle_files/241946168596.pic


If we want to see the raw data stored in the table, we can create a new doctable without a defined schema. See that the raw filenames have been stored in the database. Recall that the directory indicating where to find these files was provided in the schema itself. 


```python
vdb = doctable.DocTable(f'{tmpfolder}/test.db')
print(vdb.count())
vdb.head()
```

    2


    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')
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
      <th>id</th>
      <th>array</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>838448859815.pic</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>241946168596.pic</td>
    </tr>
  </tbody>
</table>
</div>



## Data Folder Consistency
Now we try to delete a row from the database. We can see that it was deleted as expected.


```python
db.delete(where=db['id']==1)
print(db.count())
db.head()
```

    1


    /DataDrive/code/doctable/examples/../doctable/doctable.py:495: UserWarning: Method .delete() is depricated. Please use .q.delete() instead.
      warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:408: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
      warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: TypeDecorator PickleFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)





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
      <th>array</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>[[0.6837499182333924, 0.40540705856582326, 0.6...</td>
    </tr>
  </tbody>
</table>
</div>



However, when we check the folder where the data was stored, we find that the file was, in fact, not deleted. This is the case for technical reasons.


```python
for fpath in tmpfolder.rglob('*.pic'):
    print(str(fpath))
```

    /tmp/tmpkoe57pma/matrix_pickle_files/838448859815.pic
    /tmp/tmpkoe57pma/matrix_pickle_files/241946168596.pic


We can clean up the unused files using `clean_col_files()` though. Note that the specific column to clean must be provided.


```python
db.clean_col_files('array')
for fpath in tmpfolder.rglob('*.pic'):
    print(str(fpath))
```

    /tmp/tmpkoe57pma/matrix_pickle_files/241946168596.pic


    /DataDrive/code/doctable/examples/../doctable/doctable.py:444: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: TypeDecorator PickleFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)


There may be a situation where doctable cannot find the folder associated with an existing row. We can also use `clean_col_files()` to check for missing data. This might most frequently occur when the wrong folder is specified in the schema after moving the data file folder. For example, we delete all the pickle files in the directory and then run `clean_col_files()`.


```python
[fp.unlink() for fp in tmpfolder.rglob('*.pic')]
for fpath in tmpfolder.rglob('*.pic'):
    print(str(fpath))
```


```python
# see that the exception was raised
try:
    db.clean_col_files('array')
except FileNotFoundError as e:
    print(e)
```

    These files were not found while cleaning: {'/tmp/tmpkoe57pma/matrix_pickle_files/241946168596.pic'}


## Text File Types
We can also store text files in a similar way. For this, use `TextFileCol` in the folder specification.


```python
@doctable.schema(require_slots=False)
class TextFileRow:
    id: int = doctable.IDCol()
    text: str = doctable.TextFileCol(f'{tmpfolder}/my_text_files') # will store files in the tmp directory
    
tdb = doctable.DocTable(target=f'{tmpfolder}/test_textfiles.db', schema=TextFileRow, new_db=True)
tdb.insert({'text': 'Hello world. DocTable is the most useful python package of all time.'})
tdb.insert({'text': 'Star Wars is my favorite movie.'})
tdb.head()
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:365: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:391: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:408: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
      warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: TypeDecorator TextFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)





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
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>Hello world. DocTable is the most useful pytho...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>Star Wars is my favorite movie.</td>
    </tr>
  </tbody>
</table>
</div>




```python
# and they look like text files
vdb = doctable.DocTable(f'{tmpfolder}/test_textfiles.db')
print(vdb.count())
vdb.head()
```

    2


    /DataDrive/code/doctable/examples/../doctable/doctable.py:403: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')
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
      <th>id</th>
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>509620359442.txt</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>409663648614.txt</td>
    </tr>
  </tbody>
</table>
</div>



See that the text files were created, and they look like normal text files so we can read them normally.


```python
for fpath in tmpfolder.rglob('*.txt'):
    print(f"{fpath}: {fpath.read_text()}")
```

    /tmp/tmpkoe57pma/my_text_files/409663648614.txt: Star Wars is my favorite movie.
    /tmp/tmpkoe57pma/my_text_files/509620359442.txt: Hello world. DocTable is the most useful python package of all time.



```python

```


```python

```
