# NewsGroups Dataset Vignette

In this vignette, I will show you how to create a database for storing and manipulating 

## Introduction to dataset

We will be using the [20 Newsgroups dataset](http://qwone.com/~jason/20Newsgroups/) for this vignette. This is the [sklearn website description](https://scikit-learn.org/stable/datasets/real_world.html#the-20-newsgroups-text-dataset):

_The 20 newsgroups dataset comprises around 18000 newsgroups posts on 20 topics split in two subsets: one for training (or development) and the other one for testing (or for performance evaluation). The split between the train and test set is based upon a messages posted before and after a specific date._

We use sklearn's [fetch_20newsgroups](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html#sklearn.datasets.fetch_20newsgroups) method to download and access articles from the politics newsgroup.


```python
import sklearn.datasets
newsgroups = sklearn.datasets.fetch_20newsgroups(categories=['talk.politics.guns', 'talk.politics.mideast', 'talk.politics.misc'])
newsgroups.keys(), len(newsgroups['data'])
```




    (dict_keys(['data', 'filenames', 'target_names', 'target', 'DESCR']), 1575)



This is an example of a newsgroup post.


```python
print(newsgroups['data'][0])
```

    From: golchowy@alchemy.chem.utoronto.ca (Gerald Olchowy)
    Subject: Re: Help fight the Clinton Administration's invasion of your privacy
    Organization: University of Toronto Chemistry Department
    Lines: 16
    
    In article <9308@blue.cis.pitt.edu> cjp+@pitt.edu (Casimir J Palowitch) writes:
    >The Clinton Administration wants to "manage" your use of digital
    >encryption. This includes a proposal which would limit your use of
    >encryption to a standard developed by the NSA, the technical details of 
    >which would remain classified with the government.
    >
    >This cannot be allowed to happen.
    >
    
    It is a bit unfair to call blame the Clinton Administration alone...this
    initiative was underway under the Bush Administration...it is basically
    a bipartisan effort of the establishment Demopublicans and
    Republicrats...the same bipartisan effort that brought the S&L scandal,
    and BCCI, etc.
    
    Gerald
    


It looks very similar to an email, so we will use Python's `email` package to parse the text and return a dictionary containing the various relevant fields. Our `parse_email` function shows how we can extract metadata fields like author, subject, and organization from the message, as well as the main text body.


```python
import email

def parse_newsgroup(email_text):
    message = email.message_from_string(email_text)
    return {
        'author': message['from'],
        'subject': message['Subject'],
        'organization': message['Organization'],
        'lines': int(message['Lines']),
        'text': message.get_payload(),
    }

parse_newsgroup(newsgroups['data'][0])
```




    {'author': 'golchowy@alchemy.chem.utoronto.ca (Gerald Olchowy)',
     'subject': "Re: Help fight the Clinton Administration's invasion of your privacy",
     'organization': 'University of Toronto Chemistry Department',
     'lines': 16,
     'text': 'In article <9308@blue.cis.pitt.edu> cjp+@pitt.edu (Casimir J Palowitch) writes:\n>The Clinton Administration wants to "manage" your use of digital\n>encryption. This includes a proposal which would limit your use of\n>encryption to a standard developed by the NSA, the technical details of \n>which would remain classified with the government.\n>\n>This cannot be allowed to happen.\n>\n\nIt is a bit unfair to call blame the Clinton Administration alone...this\ninitiative was underway under the Bush Administration...it is basically\na bipartisan effort of the establishment Demopublicans and\nRepublicrats...the same bipartisan effort that brought the S&L scandal,\nand BCCI, etc.\n\nGerald\n'}



## Creating a database schema

The first step will be to create a database schema that is appropriate for the newsgroup dataset by defining a container dataclass using the `@schema` decorator.  The `schema` decorator will convert the class into a [`dataclass`](https://realpython.com/python-data-classes/) with [slots](https://docs.python.org/3/reference/datamodel.html#slots) enabled (provided `__slots__ = []` is given in the definition), and inherit from `DocTableRow` to add some additional functionality. The type hints associated with each variable will be used in the schema definition for the new tables, and arguments to `Col()`, `IDCol()`, `AddedCol()`, and `UpdatedCol()` will mostly be passed to `dataclasses.field` (see [docs](https://doctable.org/ref/doctable/schemas/field_columns.html#Col) for more detail), so all dataclass functionality is maintained. The [doctable schema guide](doctable_schema.html) explains more about schema and schema object definitions. 

Here I define a `NewsgroupDoc` class to represent a single document and define `__slots__` so the decorator can automatically create a slot class. Each member variable will act as a column in our database schema, and the first variable we define is an `id` column with the defaulted value `IDCol()`. This is a special function that will translate to a schema that uses the `id` colum as the primary key and enable auto-incrementing. Because `id` is defaulted, we must default our other variables as well.

I also define a couple of methods as part of our schema class - they are ignored in the schema creation process, but allow us to manipulate the object within Python. The `author_email` property will extract just the email address from the author field. Note that even though it is a property, it is defined as a method and therefore will not be considered when creating the class schema. I also define a `classmethod` that can be used to create a new `NewsgroupDoc` from the newsgroup text - this replaces the functionality of the `parse_email` function we created above. This way, the class knows how to create itself from the raw newsgroup text.


```python
import sys
sys.path.append('..')
import doctable

import re
import email
import dataclasses

def try_int(text):
    try:
        return int(text.split()[0])
    except:
        return None


@doctable.schema
class NewsgroupDoc:
    __slots__ = []
    
    # schema columns
    id: int = doctable.IDCol()
    author: str = None
    subject: str = None
    organization: str = None
    length: int = None
    text: str = None
        
    @property
    def author_email(self, pattern=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')):
        '''Get the author\'s email address from the author field text.
        '''
        return re.search(pattern, self.author)[0]
    

    @classmethod
    def from_string(cls, newsgroup_text):
        '''Code to create a NewsGroupDoc object from the original newsgroup string.
        '''
        message = email.message_from_string(newsgroup_text)
        return cls(
            author = message['from'],
            subject = message['Subject'],
            organization = message['Organization'],
            length = len(message.get_payload()),
            text = message.get_payload(),
        )
        
        
# for example, we create a new NewsGroupDoc from the first newsgroup article
ngdoc = NewsgroupDoc.from_string(newsgroups['data'][0])
print(ngdoc.author)
ngdoc.author_email
```

    golchowy@alchemy.chem.utoronto.ca (Gerald Olchowy)





    'golchowy@alchemy.chem.utoronto.ca'



To make sure the `NewsgroupDoc` will translate to the database schema we expect, we can create a new `DocTable` object that uses it as a schema. We use the `schema` argument of the `DocTable` constructor to specify the schema, and print it below. See that most fields were translated to `VARCHAR` type fields, but `id` and `length` were translated to `INTEGER` types based on their type hints.


```python
ng_table = doctable.DocTable(target=':memory:', tabname='documents', schema=NewsgroupDoc)
ng_table.schema_table()
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
      <td>author</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>subject</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>organization</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>length</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>text</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



To better describe the data we are interested in, we now create a class that inherits from `DocTable`. This class will act as the main interface for working with our dataset. We use the `_tabname_` and `_schema_` properties to define the table name and schema so we don't need to include them in the constructor. We also define a method `count_author_emails` - we will describe the behavior of this method later.


```python
import collections

class NewsgroupTable(doctable.DocTable):
    _tabname_ = 'documents'
    _schema_ = NewsgroupDoc
    
    def count_author_emails(self, *args, **kwargs):
        author_emails = self.select('author', *args, **kwargs)
        return collections.Counter(author_emails)

```

Instead of using `target=':memory:'`, we want to create a database on our filesystem so we can store data. By default, `DocTable` uses sqlite as the database engine, so with `target` we need only specify a filename. Because this is just a demonstration, we will create the database in a temporary folder using the `tempfile` package. This database does not exist yet, so we use the `new_db` flag to indicate that a new one should be created.


```python
import tempfile

tempfolder = tempfile.TemporaryDirectory()
table_fname = f'{tempfolder.name}/tmp1.db'
ng_table = NewsgroupTable(target=table_fname, new_db=True)
ng_table.schema_table()
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
      <td>author</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>subject</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>organization</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>length</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>text</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



## Parsing and storing documents

Now we would like to parse our documents for storage in the database. It is relatively straighforward to create a list of parsed texts using the `from_string` method. After doing this, we could potentially just insert them directly into the database.


```python
%timeit [NewsgroupDoc.from_string(text) for text in newsgroups['data']]
```

    191 ms ± 527 µs per loop (mean ± std. dev. of 7 runs, 1 loop each)


This is a relatively straigtforward task with a dataset of this size, but if we had a larger dataset or used more costly parsing algorithms, we would want to distribute parsing across multiple processes - we will take that approach for demonstration. First we define the `process_and_store` class to be used in each worker process.


```python
def thread_func(numbers, db):
    print(f'starting process')
    db.reopen_engine() # create all new connections
    db.insert([{'subject': i} for  i in numbers])
    #for num in numbers:
    #    db.insert({'process': process_id, 'number': num})
    #    time.sleep(0.01)

numbers = list(range(100)) # these numbers are to be inserted into the database

ng_table.delete()
with doctable.Distribute(5) as d:
    d.map_chunk(thread_func, numbers, ng_table)
ng_table.head(10)
```

    starting process
    starting process
    starting process
    starting process
    starting process





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
      <th>author</th>
      <th>subject</th>
      <th>organization</th>
      <th>length</th>
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>None</td>
      <td>0</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>None</td>
      <td>1</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>None</td>
      <td>2</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>None</td>
      <td>3</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>None</td>
      <td>4</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>5</th>
      <td>6</td>
      <td>None</td>
      <td>5</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>6</th>
      <td>7</td>
      <td>None</td>
      <td>6</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>7</th>
      <td>8</td>
      <td>None</td>
      <td>7</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>8</th>
      <td>9</td>
      <td>None</td>
      <td>8</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <th>9</th>
      <td>10</td>
      <td>None</td>
      <td>9</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>




```python
def printer(x, table):
    print(x, table)

with doctable.WorkerPool(3, verbose=False) as p:
    assert(p.any_alive())
    print(f'av efficiency: {p.av_efficiency()}')

    p.map(printer, list(range(100)), table=ng_table)


    # test most basic map function
    #elements = list(range(100))
    #assert(pool.map(example_func, elements) == [example_func(e) for e in elements])
    print(f'av efficiency: {p.av_efficiency()}')
```


    ---------------------------------------------------------------------------

    AssertionError                            Traceback (most recent call last)

    <ipython-input-10-48aa27ce5dc0> in <module>
          3 
          4 with doctable.WorkerPool(3, verbose=False) as p:
    ----> 5     assert(p.any_alive())
          6     print(f'av efficiency: {p.av_efficiency()}')
          7 


    AssertionError: 



```python
import pickle
pickle.dumps(ng_table.schema_info)
```


```python
import multiprocessing
class parse_thread:
    def __init__(self, table: doctable.DocTable):
        self.table = table
    
    def __call__(self, texts):
        with self.table as t:
            #records = [NewsgroupDoc.from_string(text) for text in texts]
            
            t.insert(NewsgroupDoc(1000))

def parse_thread2(x):
    return None
            
chunks = doctable.chunk(newsgroups['data'], chunk_size=100)
#parse_func = parse_thread(ng_table)
with multiprocessing.Pool(4) as p:
    %time p.map(parse_thread(ng_table), chunks, 100)
#%time map(parse_thread(1), chunks)
```


```python
class process_and_store:
    table: doctable.DocTable = None
        
    def __init__(self, table_cls, *table_args, **table_kwargs):
        '''Store info to construct the table.
        '''
        self.table_cls = table_cls
        self.table_args = table_args
        self.table_kwargs = table_kwargs
        
    def connect_db(self):
        '''Make a new connection to the database and return the associated table.
        '''
        if self.table is None:
            self.table = self.table_cls(*self.table_args, **self.table_kwargs)
        return self.table
    
    def __call__(self, text):
        '''Execute function in worker process.
        '''
        table = self.connect_db()
        
        record = NewsgroupDoc.from_string(text)
        table.insert(record)
        
import multiprocessing
with multiprocessing.Pool(4) as p:
    %time p.map(process_and_store(NewsgroupTable, target=table_fname), newsgroups['data'])
```

Notice that this takes very little CPU time, but a long "wall time" (overall time it takes to run the program). This is because the threads are IO-starved - they spend a lot of time waiting on each other to commit database transactions. This might be a good opportunity to use variations on threading models, but most parsing classes 


```python
class process_and_store_chunk(process_and_store):
    def __call__(self, texts):
        '''Execute function in worker process.
        '''
        table = self.connect_db()
        
        records = [NewsgroupDoc.from_string(text) for text in texts]
        table.insert(records)

chunked_newsgroups = doctable.chunk(newsgroups['data'], chunk_size=500)
with multiprocessing.Pool(4) as p:
    %time p.map(process_and_store_chunk(NewsgroupTable, target=table_fname), chunked_newsgroups)
```


```python

```


```python

```


```python
parser = ParsePipeline([
    parse_email
])


for email_text in newsgroups['data']:
    email_data = parse_email(email_text)
```


```python


import multiprocessing
with multiprocessing.Pool(10) as p:
    print(p)
```
