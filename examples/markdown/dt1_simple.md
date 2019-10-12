# DocTable Simple Example
In this notebook, I show how to define a DocTable as a python class, populate the DocTable using the .add() and .addmany() commands, query data through generators and pandas dataframes, and finally update DocTable entries.


```python
from pprint import pprint
from timeit import default_timer as timer
from dt1_helper import get_sklearn_newsgroups

import sys
sys.path.append('..')
import doctable as dt # this will be the table object we use to interact with our database.
```

## Get News Data From sklearn.datasets
Then parses into a dataframe.


```python
ddf = get_sklearn_newsgroups()
print(ddf.info())
ddf.head(3)
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 11314 entries, 0 to 11313
    Data columns (total 3 columns):
    filename    11314 non-null object
    target      11314 non-null object
    text        11314 non-null object
    dtypes: object(3)
    memory usage: 265.3+ KB
    None





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
      <th>filename</th>
      <th>target</th>
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>21379</td>
      <td>soc.religion.christian</td>
      <td>From: kbanner@philae.sas.upenn.edu (Ken Banner...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>20874</td>
      <td>soc.religion.christian</td>
      <td>From: simon@monu6.cc.monash.edu.au\nSubject: S...</td>
    </tr>
    <tr>
      <td>2</td>
      <td>58936</td>
      <td>sci.med</td>
      <td>From: jeffp@vetmed.wsu.edu (Jeff Parke)\nSubje...</td>
    </tr>
  </tbody>
</table>
</div>



## Define DocTable Class
This class definition will contain the columns, datatypes, unique constraints, and index commands needed for your DocTable.
In moving your data from DataFrame to DocTable, you should consider column data types and custom indices carefully.


```python
# this class will represent the doctable. It inherits from DocTable a number of add/query/remove functions.
# of course, you can add any additional methods to this class definition as you find useful.
class SimpleNewsGroups(dt.DocTable):
    def __init__(self, fname):
        '''
            This includes examples of init variables. See DocTable class for complete list of options.
            Inputs:
                fname: fname is the name of the new sqlite database that will be used for this class.
        '''
        tabname = 'simplenewsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema=(
                'id integer primary key autoincrement',
                'file_id int',
                'category string',
                'raw_text string',
            )
        )
        
        # this section defines any other commands that should be executed upon init
        # NOTICE: references tabname defined in the above __init__ function
        # extra commands to create index tables for fast lookup
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")
```

Create a connection to the database by constructing an instance of the class. If this is the first time you've run this code, it will create a new sqlite database file with no entries.


```python
sng = SimpleNewsGroups('simple_news_group.db')
print(sng)
```

    <Documents ct: 0>


## Adding Data
There are two common ways to add data to your DocTable.

(1) Add in rows individually

(2) Add in bulk with or without specifying column names


```python
# adds data one row at a time. Takes longer than bulk version
start = timer()

for ind,dat in ddf.iterrows():
    row = {'file_id':int(dat['filename']), 'category':dat['target'], 'raw_text':dat['text']}
    sng.add(row, ifnotunique='replace')

print((timer() - start)*1000, 'mil sec.')
print(sng)
```

    2366.1215798929334 mil sec.
    <Documents ct: 11314>



```python
# adds tuple data in bulk by specifying columns we are adding
start = timer()

col_order = ('file_id','category','raw_text')
data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
sng.addmany(data,keys=col_order, ifnotunique='replace')

print((timer() - start)*1000, 'mil sec.')
print(sng)
```

    1893.8379744067788 mil sec.
    <Documents ct: 22628>


## Querying Data
There are two primary ways of querying data from a DocTable:

(1) retrieve one-by-one from generator using ".get()" function.
(2) retrieve all data in Pandas DataFrame suing ".getdf()" function.


```python
result = sng.get(
    sel=('file_id','raw_text'), 
    where='category == "rec.motorcycles"', 
    orderby='file_id ASC', 
    limit=3,
)
for row in result:
    print(str(row['file_id'])+':', row['raw_text'][:50])
```

    72052: From: ivan@erich.triumf.ca (Ivan D. Reid)
    Subject:
    72052: From: ivan@erich.triumf.ca (Ivan D. Reid)
    Subject:
    101725: Subject: Re: Lexan Polish?
    From: jeff@mri.com (Jon



```python
result_df = sng.getdf(
    sel=('file_id','raw_text'), 
    where='category == "rec.motorcycles"', 
    orderby='file_id ASC', 
    limit=5,
)
result_df
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
      <th>file_id</th>
      <th>raw_text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>72052</td>
      <td>From: ivan@erich.triumf.ca (Ivan D. Reid)\nSub...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>72052</td>
      <td>From: ivan@erich.triumf.ca (Ivan D. Reid)\nSub...</td>
    </tr>
    <tr>
      <td>2</td>
      <td>101725</td>
      <td>Subject: Re: Lexan Polish?\nFrom: jeff@mri.com...</td>
    </tr>
    <tr>
      <td>3</td>
      <td>101725</td>
      <td>Subject: Re: Lexan Polish?\nFrom: jeff@mri.com...</td>
    </tr>
    <tr>
      <td>4</td>
      <td>102616</td>
      <td>From: blgardne@javelin.sim.es.com (Dances With...</td>
    </tr>
  </tbody>
</table>
</div>



## Updating Data in DocTable
The ".update()" function will change entries in the DocTable.


```python
sng.update({'category':'nevermind',},where='file_id == "103121"')
sng.getdf(where='file_id == "103121"') # to see update, look at "category" column entry
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
      <th>id</th>
      <th>file_id</th>
      <th>category</th>
      <th>raw_text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>395</td>
      <td>103121</td>
      <td>nevermind</td>
      <td>From: MJMUISE@1302.watstar.uwaterloo.ca (Mike ...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>11709</td>
      <td>103121</td>
      <td>nevermind</td>
      <td>From: MJMUISE@1302.watstar.uwaterloo.ca (Mike ...</td>
    </tr>
  </tbody>
</table>
</div>


