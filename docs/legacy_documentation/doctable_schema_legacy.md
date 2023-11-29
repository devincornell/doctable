# DocTable Schemas
There are two ways to define schemas for a DocTable:

1. **dataclass schema**: column names and types come from a class created using the `@doctable.schema` decorator. This class represents a single row, and is returned by default when a select query is executed. `doctable` provides a thin layer over [dataclasses](https://realpython.com/python-data-classes/) with slots to reduce memory overhead from returned results. Custom methods can also be defined on the class that will not affect the database schema. When using this method, constraints and indices must be provided at the time of `DocTable` instantiation (or in the definition of an inheriting `DocTable`).

2. **list schema**: column names and types come from sequences of strings according to a custom doctable format. This method requires less knowledge of doctable objects but otherwise has no advantages over dataclass schemas.

The doctable package builds on sqlalchemy, so both types of schema specifications ultimately result in a sequence of [`sqlalchemy` column types](https://docs.sqlalchemy.org/en/13/core/type_basics.html) that will be used to construct (or interface with) the database table.


```python
from datetime import datetime
from pprint import pprint
import pandas as pd

import sys
sys.path.append('..')
import doctable
```

## Schema Type Mappings
There are two lookup tables used to relate to sqlalchemy column types. The first is a map from Python datatypes to the sqlalchemy types. This is sufficient for the simplest possible dataclass schema specification.

The second is a string lookup that is provided for the list schema format. You can see that this offers a larger number of types compared to the Python type conversion.

There are several other custom column types I included for convenience.


```python
doctable.string_to_sqlalchemy_type
```




    {'biginteger': sqlalchemy.sql.sqltypes.BigInteger,
     'boolean': sqlalchemy.sql.sqltypes.Boolean,
     'date': sqlalchemy.sql.sqltypes.Date,
     'datetime': sqlalchemy.sql.sqltypes.DateTime,
     'enum': sqlalchemy.sql.sqltypes.Enum,
     'float': sqlalchemy.sql.sqltypes.Float,
     'integer': sqlalchemy.sql.sqltypes.Integer,
     'interval': sqlalchemy.sql.sqltypes.Interval,
     'largebinary': sqlalchemy.sql.sqltypes.LargeBinary,
     'numeric': sqlalchemy.sql.sqltypes.Numeric,
     'smallinteger': sqlalchemy.sql.sqltypes.SmallInteger,
     'string': sqlalchemy.sql.sqltypes.String,
     'text': sqlalchemy.sql.sqltypes.Text,
     'time': sqlalchemy.sql.sqltypes.Time,
     'unicode': sqlalchemy.sql.sqltypes.Unicode,
     'unicodetext': sqlalchemy.sql.sqltypes.UnicodeText,
     'json': doctable.schemas.custom_coltypes.JSONType,
     'pickle': doctable.schemas.custom_coltypes.CpickleType,
     'parsetree': doctable.schemas.custom_coltypes.ParseTreeDocFileType,
     'picklefile': doctable.schemas.custom_coltypes.PickleFileType,
     'textfile': doctable.schemas.custom_coltypes.TextFileType}



## List Schemas
And this is another example showing the list schema format.


```python
schema = (
    # standard id column
    #SQLAlchemy: Column('id', Integer, primary_key = True, autoincrement=True), 
    ('integer', 'id', dict(primary_key=True, autoincrement=True)),
    # short form (can't provide any additional args though): ('idcol', 'id')

    # make a category column with two options: "FICTION" and "NONFICTION"
    #SQLAlchemy: Column('title', String,)
    ('string', 'category', dict(nullable=False)),

    # make a non-null title column
    #SQLAlchemy: Column('title', String,)
    ('string', 'title', dict(nullable=False)),

    # make an abstract where the default is an empty string instead of null
    #SQLAlchemy: Column('abstract', String, default='')
    ('string', 'abstract',dict(default='')),

    # make an age column where age must be greater than zero
    #SQLAlchemy: Column('abstract', Integer)
    ('integer', 'age'),

    # make a column that keeps track of column updates
    #SQLAlchemy: Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
    ('datetime', 'updated_on',  dict(default=datetime.now, onupdate=datetime.now)),
    # short form to auto-record update date: ('date_updated', 'updated_on')
    
    #SQLAlchemy: Column('updated_on', DateTime(), default=datetime.now)
    ('datetime', 'updated_on',  dict(default=datetime.now)),
    # short form to auto-record insertion date: ('date_added', 'added_on')

    # make a string column with max of 500 characters
    #SQLAlchemy: Column('abstract', String, default='')
    ('string', 'text',dict(),dict(length=500)),

    
    ##### Custom DocTable Column Types #####
    
    # uses json.dump to convert python object to json when storing and
    # json.load to convert json back to python when querying
    ('json','json_data'),
    
    # stores pickled python object directly in table as BLOB
    # TokensType and ParagraphsType are defined in doctable/coltypes.py
    # SQLAlchemy: Column('tokenized', TokensType), Column('sentencized', ParagraphsType)
    ('pickle','tokenized'),
    
    # store pickled data into a separate file, recording only filename directly in table
    # the 'fpath' argument can specify where the files should be placed, but by
    # default they are stored in <dbname>_<tablename>_<columnname>
    #('picklefile', 'pickle_obj', dict(), dict(fpath='folder_for_picklefiles')),
    
    # very similar to above, but use only when storing text data
    #('textfile', 'text_file'), # similar to above
    
    
    ##### Constraints #####
    
    #SQLAlchemy: CheckConstraint('category in ("FICTION","NONFICTION")', name='salary_check')
    ('check_constraint', 'category in ("FICTION","NONFICTION")', dict(name='salary_check')),
    
    #SQLAlchemy: CheckConstraint('age > 0')
    ('check_constraint', 'age > 0'),
    
    # make sure each category/title entry is unique
    #SQLAlchemy:  UniqueConstraint('category', 'title', name='work_key')
    ('unique_constraint', ['category','title'], dict(name='work_key')),
    
    # makes a foreign key from the 'subkey' column of this table to the 'id'
    # column of ANOTHERDOCTABLE, setting the SQL onupdate and ondelete foreign key constraints
    #('foreignkey_constraint', [['subkey'], [ANOTHERDOCTABLE['id']]], {}, dict(onupdate="CASCADE", ondelete="CASCADE")),
    #NOTE: Can't show here because we didn't make ANOTHERDOCTABLE
    
    ##### Indexes ######
    
    # make index table
    # SQLAlchemy: Index('ind0', 'category', 'title', unique=True)
    ('index', 'ind0', ('category','title'),dict(unique=True)),
    
)
md = doctable.DocTable(target=':memory:', schema=schema, verbose=True)
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
      <td>id</td>
      <td>INTEGER</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>category</td>
      <td>VARCHAR</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>title</td>
      <td>VARCHAR</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>abstract</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>age</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>updated_on</td>
      <td>DATETIME</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>text</td>
      <td>VARCHAR(500)</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>json_data</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>tokenized</td>
      <td>BLOB</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>


