# ParseTreeDoc Column Types
Creating parsetrees with spacy can be a computationally expensive task, so we may often want to store them in a database for better use. Because they may be large binary files, we will store them as pickle file column types, but with an additional serialization step.


```python
import spacy
nlp = spacy.load('en_core_web_sm')
import numpy as np
from pathlib import Path

import sys
sys.path.append('..')
import doctable

# automatically clean up temp folder after python ends
import tempfile
tempdir = tempfile.TemporaryDirectory()
tmpfolder = tempdir.name
tmpfolder

import tempfile
with tempfile.TemporaryDirectory() as tmp:
    print(tmp)
```

    /tmp/tmpnmvhkw9t


Create some test data and make a new `ParseTreeDoc` object.


```python
texts = [
    'Help me Obi-Wan Kenobi. You’re my only hope. ',
    'I find your lack of faith disturbing. ',
    'Do, or do not. There is no try. '
]
parser = doctable.ParsePipeline([nlp, doctable.Comp('get_parsetrees')])
docs = parser.parsemany(texts)
for doc in docs:
    print(len(doc))
```

    2
    1
    2


Now we create a schema that includes the `doc` column and the `ParseTreeFileCol` default value. Notice that using the type hint `ParseTreeDoc` and giving a generic `Col` default value is also sufficient.


```python
import dataclasses
@doctable.schema(require_slots=False)
class DocRow:
    id: int = doctable.IDCol()
    doc: doctable.ParseTreeDoc = doctable.ParseTreeFileCol(f'{tmpfolder}/parsetree_pickle_files')
        
    # could also use this:
    #doc: doctable.ParseTreeDoc = doctable.Col(type_args=dict(folder=f'{tmp}/parsetree_pickle_files'))
    
db = doctable.DocTable(target=f'{tmpfolder}/test_ptrees.db', schema=DocRow, new_db=True)
db.schema_info()
```




    [{'name': 'id',
      'type': INTEGER(),
      'nullable': False,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 1},
     {'name': 'doc',
      'type': VARCHAR(),
      'nullable': True,
      'default': None,
      'autoincrement': 'auto',
      'primary_key': 0}]




```python
#db.insert([{'doc':doc} for doc in docs])
for doc in docs:
    db.insert({'doc': doc})
db.head(3)
```

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
      <th>3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>3</td>
    </tr>
  </tbody>
</table>
</div>




```python
for idx, doc in db.q.select_raw():
    print(f"doc id {idx}:")
    for i, sent in enumerate(doc):
        print(f"\tsent {i}: {[t.text for t in sent]}")
```

    doc id 1:
    	sent 0: ['Help', 'me', 'Obi', '-', 'Wan', 'Kenobi', '.']
    	sent 1: ['You', '’re', 'my', 'only', 'hope', '.']
    doc id 2:
    	sent 0: ['I', 'find', 'your', 'lack', 'of', 'faith', 'disturbing', '.']
    doc id 3:
    	sent 0: ['Do', ',', 'or', 'do', 'not', '.']
    	sent 1: ['There', 'is', 'no', 'try', '.']


    /DataDrive/code/doctable/examples/../doctable/connectengine.py:70: SAWarning: TypeDecorator ParseTreeDocFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)


See that the files exist, and we can remove/clean them just as any other file column type.


```python
for fpath in Path(tmpfolder).rglob('*.pic'):
    print(str(fpath))
```

    /tmp/tmpvmthfr7t/parsetree_pickle_files/347692105083_parsetreedoc.pic
    /tmp/tmpvmthfr7t/parsetree_pickle_files/98072534351_parsetreedoc.pic
    /tmp/tmpvmthfr7t/parsetree_pickle_files/689952128879_parsetreedoc.pic



```python
db.delete(db['id']==1)
for fpath in Path(tmpfolder).rglob('*.pic'):
    print(str(fpath))
db.head()
```

    /tmp/tmpvmthfr7t/parsetree_pickle_files/347692105083_parsetreedoc.pic
    /tmp/tmpvmthfr7t/parsetree_pickle_files/98072534351_parsetreedoc.pic
    /tmp/tmpvmthfr7t/parsetree_pickle_files/689952128879_parsetreedoc.pic


    /DataDrive/code/doctable/examples/../doctable/doctable.py:506: UserWarning: Method .delete() is depricated. Please use .q.delete() instead.
      warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')
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
      <th>doc</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>[(I, find, your, lack, of, faith, disturbing, .)]</td>
    </tr>
    <tr>
      <th>1</th>
      <td>3</td>
      <td>[(Do, ,, or, do, not, .), (There, is, no, try,...</td>
    </tr>
  </tbody>
</table>
</div>




```python
db.clean_col_files('doc')
for fpath in Path(tmpfolder).rglob('*.pic'):
    print(str(fpath))
```

    /tmp/tmpvmthfr7t/parsetree_pickle_files/347692105083_parsetreedoc.pic
    /tmp/tmpvmthfr7t/parsetree_pickle_files/98072534351_parsetreedoc.pic


    /DataDrive/code/doctable/examples/../doctable/doctable.py:449: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:70: SAWarning: TypeDecorator ParseTreeDocFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)

