# DocTable Example: Schemas
In this example, we show column specifications for each available type, as well as the [sqlalchemy equivalents](https://docs.sqlalchemy.org/en/13/core/type_basics.html) on which they were based. Note that .

Each column in the schema passed to doctable is a 2+ tuple containing, in order, the column type, name, and arguments, and optionally the sqlalchemy type arguemnts.


```python
from datetime import datetime
from pprint import pprint
import pandas as pd
import typing

import sys
sys.path.append('..')
import doctable
```


```python
@doctable.schema
class MyClass:
    __slots__ = []
    # builtin column types
    idx: int = doctable.IDCol()
        
    # unique name
    name: str = doctable.Col(unique=True) # want to be the first ordered argument

    
    # special columns for added and updated
    updated: datetime = doctable.UpdatedCol()
    added: datetime = doctable.AddedCol()

    # custom column types 
    lon: float = doctable.Col()
    lat: float = doctable.Col()

    # use Col to use factory to construct emtpy list
    # will be stored as binary/pickle type, since no other available
    elements: doctable.JSONType = doctable.Col(field_kwargs=dict(default_factory=list))
    
class MyTable(doctable.DocTable):
    _schema_ = MyClass
    # indices and constraints
    _indices = (
        doctable.Index('lonlat_index', 'lon', 'lat', unique=True),
        doctable.Index('name_index', 'name'),
    )
    _constraints_ = (
        doctable.Constraint('check', 'lon > 0', name='check_lon'),
        doctable.Constraint('check', 'lat > 0'),
    )


md = MyTable(target=':memory:', verbose=True)
#pprint(md.schemainfo)
md.schema_table()
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
      <th>name</th>
      <th>type</th>
      <th>nullable</th>
      <th>default</th>
      <th>autoincrement</th>
      <th>primary_key</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>idx</td>
      <td>INTEGER</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>name</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>updated</td>
      <td>DATETIME</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>added</td>
      <td>DATETIME</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>lon</td>
      <td>FLOAT</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>lat</td>
      <td>FLOAT</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>elements</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python

```
