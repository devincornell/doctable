# Vignette 1: Storing Document Metadata
In this example, I'll show how to create and manipulate two linked tables for storing document metadata using [US National Security Strategy document](https://github.com/devincornell/nssdocs) metadata as an example. 

These are the vignettes I have created:

+ [1: Storing Document Metadata](example_nss_1_intro.html)

+ [2: Storing Document Text](example_nss_2_parsing.html)

+ [3: Storing Parsed Documents](example_nss_3_parsetrees.html)


```python
import sys
sys.path.append('..')
import doctable
import spacy
from tqdm import tqdm
import pandas as pd
import os
from pprint import pprint
import urllib.request # used for downloading nss docs

# automatically clean up temp folder after python ends
#tmpfolder = doctable.TempFolder('tmp')
import tempfile
tempdir = tempfile.TemporaryDirectory()
tmpfolder = tempdir.name
tmpfolder
```




    '/tmp/tmplxxguo16'



## Introduction to NSS Corpus
This dataset is the plain text version of the US National Security Strategy documents. I compiled the metadata you see below from [a page hosted by the historical dept of the secretary's office](https://history.defense.gov/Historical-Sources/National-Security-Strategy/). In short, each US President must release at least one NSS per term, up to one per-year. This is the metadata we will be inserting into the table:


```python
# information about each NSS document
document_metadata = [
    {'year': 2000, 'party': 'D', 'president': 'Clinton'},
    {'year': 2002, 'party': 'R', 'president': 'W. Bush'}, 
    {'year': 2006, 'party': 'R', 'president': 'W. Bush'}, 
    {'year': 2010, 'party': 'D', 'president': 'Obama'}, 
    {'year': 2015, 'party': 'D', 'president': 'Obama'}, 
    {'year': 2017, 'party': 'R', 'president': 'Trump'}, 
]
```

## Create database schemas

The first step will be to define a database schema that is appropriate for the data in `document_metadata`. We define an `NSSDoc` class to represent a single document. The `doctable.schema` decorator will convert the row objects into [`dataclasses`](https://realpython.com/python-data-classes/) with [slots](https://docs.python.org/3/reference/datamodel.html#slots) enabled, and inherit from doctable.DocTableRow to add some additional functionality. The type hints associated with each variable will be used in the schema definition for the new tables, and arguments to `doctable.Col` will mostly be passed to `dataclasses.field` (see [docs](https://doctable.org/ref/doctable/schemas/field_columns.html#Col) for more detail), so all dataclass functionality is maintained.

Also note that a method called `.is_old()` was defined. This method will not be included in a database schema, but I'll show later how it can be useful.


```python
# to be used as a database row representing a single NSS document
@doctable.schema
class NSSDoc:
    __slots__ = [] # include so that doctable.schema can create a slot class
    
    id: int = doctable.Col(primary_key=True, autoincrement=True) # can also use doctable.IDCol() as a shortcut
    year: int =  None
    party: str = None
    president: str = None
        
    def is_old(self):
        '''Return whether the document is old or not.'''
        return self.year < 2010
```

We can see that these are regular dataclass methods because their constructors are defined. Note that the dataclass defaults the values to None, so take note of this when inserting or retrieving from a database.


```python
NSSDoc(year=1999)
```




    NSSDoc(year=1999, party=None, president=None)



And we will also likely want to create a class that inherits from `DocTable` to statically define the table name, schema object, and any indices or constraints that should be associated with our table. We set the table name and the schema definition class using the reserved member variables `_tabname_` and `_schema_`, respectively. Note that the `NSSDoc` class is provided as the schema.

We also can use this definition to create indices and constraints using the `_indices_` and `_constraints_` member variables. The indices are provided as name->columns pairs, and the constraints are tuples of the form `(constraint_type, constraint_details)`. In this case, we limit the values for `check` to R or D.


```python
class NSSDocTable(doctable.DocTable):
    _tabname_ = 'nss_documents'
    _schema_ = NSSDoc
    _indices_ = (
        doctable.Index('party_index', 'party'),
    )
    _constraints_ = (
        doctable.Constraint('check', 'party in ("R", "D")'), # party can only take on values R or D.
    )
```

And then we create an instance of the `NSSDocTable` table using `DocTable`\'s default constructor. We set `target=f'{tmp}/nss_1.db'` to indicate we want to access an sqlite database at that path. We also use the `new_db=True` to indicate that the database does not exist, so we should create a new one.


```python
fname = f'{tmpfolder}/nss_1.db'

# clean up any old databases
try:
    os.remove(fname)
except:
    pass

docs_table = NSSDocTable(target=fname, new_db=True)
docs_table
```




    <__main__.NSSDocTable at 0x7f2a55b9b400>



We can use `.schema_table()` to see information about the database schema. Note that doctable inferred column types based on the type hints.


```python
docs_table.schema_table()
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
      <td>year</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>party</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>president</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



We are now ready to insert data into the new table. We simply add each document as a dictionary, and show the first `n` rows using `.head()`.


```python
docs_table.delete() # remove old entries if needed
for doc in document_metadata:
    print(doc)
    docs_table.insert(doc)
docs_table.head()
```

    {'year': 2000, 'party': 'D', 'president': 'Clinton'}
    {'year': 2002, 'party': 'R', 'president': 'W. Bush'}
    {'year': 2006, 'party': 'R', 'president': 'W. Bush'}
    {'year': 2010, 'party': 'D', 'president': 'Obama'}
    {'year': 2015, 'party': 'D', 'president': 'Obama'}
    {'year': 2017, 'party': 'R', 'president': 'Trump'}


    /DataDrive/code/doctable/examples/../doctable/doctable.py:494: UserWarning: Method .delete() is depricated. Please use .q.delete() instead.
      warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:364: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:390: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:407: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
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
      <th>year</th>
      <th>party</th>
      <th>president</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2000</td>
      <td>D</td>
      <td>Clinton</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2002</td>
      <td>R</td>
      <td>W. Bush</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2006</td>
      <td>R</td>
      <td>W. Bush</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>2010</td>
      <td>D</td>
      <td>Obama</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>2015</td>
      <td>D</td>
      <td>Obama</td>
    </tr>
  </tbody>
</table>
</div>



We can verify that the constraint was defined by attempting to insert a row with an unknown party code.


```python
import sqlalchemy
try:
    docs_table.insert({'party':'whateva'})
except sqlalchemy.exc.IntegrityError as e:
    print(e)
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:364: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:390: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '


And we can use all the expected select (see [select examples](doctable_select.html)) methods.


```python
democrats = docs_table.select(where=docs_table['party']=='D')
democrats
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:443: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')





    [NSSDoc(id=1, year=2000, party='D', president='Clinton'),
     NSSDoc(id=4, year=2010, party='D', president='Obama'),
     NSSDoc(id=5, year=2015, party='D', president='Obama')]




```python
clinton_doc = docs_table.select_first(where=docs_table['president']=='Clinton')
clinton_doc
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:426: UserWarning: Method .select_first() is depricated. Please use .q.select_first() instead.
      warnings.warn('Method .select_first() is depricated. Please use .q.select_first() instead.')





    NSSDoc(id=1, year=2000, party='D', president='Clinton')



Along with the methods we defined on the schema objects.


```python
clinton_doc.is_old()
```




    True



## Adding political party data

Of course, relational database schemas often involve the use of more than one linked table. Now we'll attempt to integrate the data in `party_metadata` into our schema.


```python
# full name of party (we will use later)
party_metadata = [
    {'code': 'R', 'name': 'Republican'},
    {'code': 'D', 'name': 'Democrat'},
]
```

First, we create the `Party` dataclass just as before.


```python
# to be used as a database row representing a single political party
@doctable.schema
class Party:
    __slots__ = []
    
    id: int = doctable.Col(primary_key=True, autoincrement=True) # can also use doctable.IDCol() as a shortcut    
    code: str = None
    name: str = None
```

And then define a `DocTable` with a 'foreignkey' constraint that indicates it\'s relationship to the document table. We can use the reference to the "party" column using `nss_documents.party`.


```python
class PartyTable(doctable.DocTable):
    _tabname_ = 'political_parties'
    _schema_ = Party
    _indices_ = {
        doctable.Index('code_index', 'code')
    }
    _constraints_ = (
        doctable.Constraint('foreignkey', ('code',), ('nss_documents.party',)),
    )

party_table = PartyTable(target=fname)
party_table
```




    <__main__.PartyTable at 0x7f2a55afa310>




```python
party_table.delete() # remove old entries if needed
for party in party_metadata:
    print(party)
    party_table.insert(party)
party_table.head()
```

    {'code': 'R', 'name': 'Republican'}
    {'code': 'D', 'name': 'Democrat'}


    /DataDrive/code/doctable/examples/../doctable/doctable.py:494: UserWarning: Method .delete() is depricated. Please use .q.delete() instead.
      warnings.warn('Method .delete() is depricated. Please use .q.delete() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:407: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
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
      <th>code</th>
      <th>name</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>R</td>
      <td>Republican</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>D</td>
      <td>Democrat</td>
    </tr>
  </tbody>
</table>
</div>



## Performing "join" select queries

In contrast to sql, the type of join is inferred from the way the select query is used. Using a `select` method with columns for both tables will issue an outer join in lieu of other parameters. Also note that we must use `as_dataclass` to indicate the data should not use a dataclass for the results, since joined results includes fields from both 


```python
party_table.select(['name', docs_table['president']], as_dataclass=False)
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:443: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')
    /DataDrive/code/doctable/examples/../doctable/doctable.py:445: UserWarning: The "as_dataclass" parameter has been depricated: please set get_raw=True or select_raw to specify that you would like to retrieve a raw RowProxy pobject.
      warnings.warn(f'The "as_dataclass" parameter has been depricated: please set get_raw=True or '
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: SELECT statement has a cartesian product between FROM element(s) "nss_documents" and FROM element "political_parties".  Apply join condition(s) between each element to resolve.
      return self._engine.execute(query, *args, **kwargs)
    /DataDrive/code/doctable/examples/../doctable/doctable.py:453: UserWarning: Conversion from row to object failed according to the following error. Please use .q.select_raw() next time in the future to avoid this issue. e=RowDataConversionFailed("Conversion from <class 'sqlalchemy.engine.row.LegacyRow'> to <class '__main__.Party'> failed.")
      warnings.warn(f'Conversion from row to object failed according to the following '





    [('Republican', 'Clinton'),
     ('Republican', 'W. Bush'),
     ('Republican', 'W. Bush'),
     ('Republican', 'Obama'),
     ('Republican', 'Obama'),
     ('Republican', 'Trump'),
     ('Republican', None),
     ('Democrat', 'Clinton'),
     ('Democrat', 'W. Bush'),
     ('Democrat', 'W. Bush'),
     ('Democrat', 'Obama'),
     ('Democrat', 'Obama'),
     ('Democrat', 'Trump'),
     ('Democrat', None)]



To perform an inner join, use a where conditional indicating the columns to be matched.


```python
docs_table.select(['year', 'president', party_table['name']], as_dataclass=False, where=docs_table['party']==party_table['code'])
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:453: UserWarning: Conversion from row to object failed according to the following error. Please use .q.select_raw() next time in the future to avoid this issue. e=RowDataConversionFailed("Conversion from <class 'sqlalchemy.engine.row.LegacyRow'> to <class '__main__.NSSDoc'> failed.")
      warnings.warn(f'Conversion from row to object failed according to the following '





    [(2000, 'Clinton', 'Democrat'),
     (2002, 'W. Bush', 'Republican'),
     (2006, 'W. Bush', 'Republican'),
     (2010, 'Obama', 'Democrat'),
     (2015, 'Obama', 'Democrat'),
     (2017, 'Trump', 'Republican')]



And this works approximately the same when we switch the tables being selected.


```python
party_table.select(['code', 'name', docs_table['president']], as_dataclass=False, where=docs_table['party']==party_table['code'])
```




    [('R', 'Republican', 'Trump'),
     ('R', 'Republican', 'W. Bush'),
     ('R', 'Republican', 'W. Bush'),
     ('D', 'Democrat', 'Clinton'),
     ('D', 'Democrat', 'Obama'),
     ('D', 'Democrat', 'Obama')]



And that is all for this vignette! See the list of vignettes at the top of this page for more examples.
