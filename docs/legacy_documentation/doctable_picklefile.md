# DocTable Example: Pickle and Text Files
Here I show a bit about how to use `picklefile` and `textfile` column types. DocTable transparently handles saving and reading column data as separate files when data is large to improve performance of select queries. It will automatically create a folder in the same directory as your sqlite database and save or read file data as if you were working with a regular table entry.


```python
import os
import sys
sys.path.append('..')
import doctable
```


```python
#tmp = doctable.TempFolder('./tmp') # will delete folder upon destruction
import tempfile
import pathlib
fkasdfjlaj = tempfile.TemporaryDirectory()
tmp = fkasdfjlaj.name

# create column schema: each row corresponds to a pickle
import dataclasses
@doctable.schema(require_slots=False)
class FileEntry:
    pic: list = doctable.Col(column_type='picklefile', type_kwargs=dict(folder=tmp))
    idx: int = doctable.IDCol()
    
db = doctable.DocTable(schema=FileEntry, target=':memory:')
```

First we try inserting a basic object, where the data will be stored in a pickle file. We can see from the `select` statement that the data read/write is handled transparently by doctable.


```python
a = [1, 2, 3, 4, 5]
db.insert(FileEntry(a))
db.select() # regular select using the picklefile datatype
```

    BINDING MF PARAMSSSSSSS
    PROCESSING MF PARAMSSSSSSS





    [FileEntry(pic=[1, 2, 3, 4, 5], idx=1)]



We can also try turning off the transparent conversion, and instead retrieve the regular directory.


```python
with db['pic'].type.control:
    r = db.select()
r
```

    PROCESSING MF PARAMSSSSSSS





    [FileEntry(pic=f'{tmp}/564814847383.pic', idx=1)]



For performance reasons, DocTable never deletes stored file data unless you call the `.clean_col_files()` method directly. It will raise an exception if a referenced file is missing, and delete all files which are not referenced in the table. This is a costly function call, but a good way to make sure your database is 1-1 matched with your filesystem.


```python
# deletes files not in db and raise error if some db files not in filesystem
db.clean_col_files('pic')
```

    PROCESSING MF PARAMSSSSSSS


Now I create another DocTable with a changed `fpath` argument. Because the argument changed, DocTable will raise an exception when selecting or calling `.clean_col_files()`. Be wary of this!
