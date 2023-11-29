# Example 1: US National Security Strategy Document Corpus
In this example, I'll show how to create a database for document + metadata storage using the `DocTable` class, and a parser class using a `ParsePipeline`. We will store the metadata you see below with the raw text and parsed tokens in the same DocTable.


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
```

## Introduction to NSS Corpus
This dataset is the plain text version of the US National Security Strategy documents. During the parsing process, all plain text files will be downloaded from my [github project hosting the nss docs](https://github.com/devincornell/nssdocs). I compiled the metadata you see below from [a page hosted by the historical dept of the secretary's office](https://history.defense.gov/Historical-Sources/National-Security-Strategy/). In short, each US President must release at least one NSS per term, with some (namely Clinton) producing more.

Here I've created the function `download_nss` to download the text data from my nssdocs github repository, and the python dictionary `nss_metadata` to store information about each document to be stored in the database.


```python
def download_nss(year):
    ''' Simple helper function for downloading texts from my nssdocs repo.'''
    baseurl = 'https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/{}.txt'
    url = baseurl.format(year)
    text = urllib.request.urlopen(url).read().decode('utf-8')
    return text
```


```python
nss_metadata = {
    1987: {'party': 'R', 'president': 'Reagan'}, 
    1993: {'party': 'R', 'president': 'H.W. Bush'}, 
    2002: {'party': 'R', 'president': 'W. Bush'}, 
    2015: {'party': 'D', 'president': 'Obama'}, 
    1994: {'party': 'D', 'president': 'Clinton'}, 
    1990: {'party': 'R', 'president': 'H.W. Bush'}, 
    1991: {'party': 'R', 'president': 'H.W. Bush'}, 
    2006: {'party': 'R', 'president': 'W. Bush'}, 
    1997: {'party': 'D', 'president': 'Clinton'}, 
    1995: {'party': 'D', 'president': 'Clinton'}, 
    1988: {'party': 'R', 'president': 'Reagan'}, 
    2017: {'party': 'R', 'president': 'Trump'}, 
    1996: {'party': 'D', 'president': 'Clinton'}, 
    2010: {'party': 'D', 'president': 'Obama'}, 
    1999: {'party': 'D', 'president': 'Clinton'}, 
    1998: {'party': 'D', 'president': 'Clinton'}, 
    2000: {'party': 'D', 'president': 'Clinton'}
}
```


```python
# downloader example: first 100 characters of 1993 NSS document
text = download_nss(1993)
text[:100]
```




    'Preface \n\nAmerican Leadership for Peaceful Change \n\nOur great Nation stands at a crossroads in histo'



## 1. Create a DocTable Schema
The `DocTable` class is often used by subclassing. Our `NSSDocs` class inherits from `DocTable` and will store connection and schema information. Because the default constructor checks for statically define member variables `tabname` and `schema` (as well as others), we can simply add them to the class definition. 

In this example, we create the 'id' column as a unique index, the 'year', 'president', and 'party' columns for storing the metadata we defined above in `nss_metadata`, and columns for raw and parse text. See the [schema guide](examples/doctable_schema.html) for examples of the full range of column types.


```python
from dataclasses import dataclass
from typing import Any

@doctable.schema(require_slots=False)
class NSSDoc:
    id: int = doctable.IDCol()
    year: int = doctable.Col(nullable=False)
    president: str = doctable.Col()
    party: str = doctable.Col()
    text: str = doctable.Col()
    parsed: Any = doctable.Col()

```

We can then create a connection to a database by instantiating the `NSSDocs` class. Since the `fname` parameter was not provided, this doctable exists only in memory using sqlite (uses special sqlite name ":memory:"). We will use this for these examples.

We can check the sqlite table schema using `.schema_table()`. You can see that the 'pickle' datatype we chose above is represented as a BLOB column. This is because DocTable, using SQLAlchemy core, creates an interface on top of sqlite to handle the data conversion. You can view the number of documents using `.count()` or by viewing the db instance as a string (in this case with print function).


```python
# printing the DocTable object itself shows how many entries there are
db = doctable.DocTable(schema=NSSDoc, target=':memory:', verbose=True)
print(db.count())
print(db)
db.schema_table()
```

    DocTable: SELECT count() AS count_1 
    FROM _documents_
     LIMIT ? OFFSET ?
    0
    <DocTable (6 cols)::sqlite:///:memory::_documents_>





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
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>president</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>party</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>text</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>parsed</td>
      <td>BLOB</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



## 2. Insert Data Into the Table

Now let's download and store the text into the database. Each loop downloads a text document and inserts it into the doctable, and we use the `.insert()` method to insert a single row at a time. The row to be inserted is represented as a dictionary, and any missing column information is left as NULL. The `ifnotunique` argument is set to false because if we were to re-run this code, it needs to replace the existing document of the same year. Recall that in the schema we placed a unique constraint on the year column.


```python
for year, docmeta in tqdm(nss_metadata.items()):
    text = download_nss(year)
    new_doc = NSSDoc(
        year=year, 
        party=docmeta['party'], 
        president=docmeta['president'], 
        text=text
    )
    db.insert(new_doc, ifnotunique='replace', verbose=False)
db.head()
```

    100%|██████████| 17/17 [00:01<00:00, 12.31it/s]

    DocTable: SELECT _documents_.id, _documents_.year, _documents_.president, _documents_.party, _documents_.text, _documents_.parsed 
    FROM _documents_
     LIMIT ? OFFSET ?


    





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
      <th>president</th>
      <th>party</th>
      <th>text</th>
      <th>parsed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>1987</td>
      <td>Reagan</td>
      <td>R</td>
      <td>I. An American Perspective \n\nIn the early da...</td>
      <td>[[I., An, American, Perspective], [in, the, ea...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>1993</td>
      <td>H.W. Bush</td>
      <td>R</td>
      <td>Preface \n\nAmerican Leadership for Peaceful C...</td>
      <td>[[preface], [American, leadership, for, peacef...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2002</td>
      <td>W. Bush</td>
      <td>R</td>
      <td>The great struggles of the twentieth century b...</td>
      <td>[[the, great, struggles, of, the, twentieth, c...</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>2015</td>
      <td>Obama</td>
      <td>D</td>
      <td>Today, the United States is stronger and bette...</td>
      <td>[[Today, ,, the, United, States, is, stronger,...</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>1994</td>
      <td>Clinton</td>
      <td>D</td>
      <td>Preface \n\nProtecting our nation's security -...</td>
      <td>[[preface], [protecting, our, nation, 's, secu...</td>
    </tr>
  </tbody>
</table>
</div>



## 3. Query Table Data
Now that we have inserted the NSS documents into the table, there are a few ways we can query the data. To select the first entry of the table use `.select_first()`. This method returns a simple `sqlalchemy.RowProxy` object which can be accessed like a dictionary or like a tuple.


```python
row = db.select_first()
#print(row)
print(row['president'])
```

    DocTable: SELECT _documents_.id, _documents_.year, _documents_.president, _documents_.party, _documents_.text, _documents_.parsed 
    FROM _documents_
     LIMIT ? OFFSET ?
    Reagan


To select more than one row, use the `.select()` method. If you'd only like to return the first few rows, you can use the `limit` argument.


```python
rows = db.select(limit=2)
print(rows[0]['year'])
print(rows[1]['year'])
```

    DocTable: SELECT _documents_.id, _documents_.year, _documents_.president, _documents_.party, _documents_.text, _documents_.parsed 
    FROM _documents_
     LIMIT ? OFFSET ?
    1987
    1993


We can also select only a few columns.


```python
db.select(['year', 'president'], limit=3)
```

    DocTable: SELECT _documents_.year, _documents_.president 
    FROM _documents_
     LIMIT ? OFFSET ?





    [NSSDoc(year=1987, president='Reagan'),
     NSSDoc(year=1993, president='H.W. Bush'),
     NSSDoc(year=2002, president='W. Bush')]



For convenience, we can also use the `.select_df()` method to return directly as a pandas dataframe.


```python
# use select_df to show a couple rows of our database
db.select_df(limit=2)
```

    DocTable: SELECT _documents_.id, _documents_.year, _documents_.president, _documents_.party, _documents_.text, _documents_.parsed 
    FROM _documents_
     LIMIT ? OFFSET ?





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
      <th>president</th>
      <th>party</th>
      <th>text</th>
      <th>parsed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>1987</td>
      <td>Reagan</td>
      <td>R</td>
      <td>I. An American Perspective \n\nIn the early da...</td>
      <td>[[I., An, American, Perspective], [in, the, ea...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>1993</td>
      <td>H.W. Bush</td>
      <td>R</td>
      <td>Preface \n\nAmerican Leadership for Peaceful C...</td>
      <td>[[preface], [American, leadership, for, peacef...</td>
    </tr>
  </tbody>
</table>
</div>



## 4. Create a Parser for Tokenization
Now that the text is in the doctable, we can extract it using `.select()`, parse it, and store the parsed text back into the table using `.update()`.

Now we create a parser using `ParsePipeline` and a list of functions to apply to the text sequentially. The `Comp` function returns a [doctable parse function](ref/doctable.parse.html) with additional keyword arguments. For instance, the following two expressions would be the same.
```
doctable.component('keep_tok', keep_punct=True) # is equivalent to
lambda x: doctable.parse.parse_tok_func(x, keep_punct=True)
```
Note in this example that the 'tokenize' function takes two function arguments `keep_tok_func` and `parse_tok_func` which are also specified using the `.Comp()` function. The available pipeline components are listed in the [parse function documentation](ref/doctable.parse.html).


```python
# first load a spacy model
nlp = spacy.load('en_core_web_sm')

# add pipeline components
parser = doctable.ParsePipeline([
    nlp, # first run spacy parser
    doctable.Comp('tokenize', **{
        'split_sents': False,
        'keep_tok_func': doctable.Comp('keep_tok'),
        'parse_tok_func': doctable.Comp('parse_tok'),
    })
])

parser.components
```




    [<spacy.lang.en.English at 0x7f2cd9334400>,
     functools.partial(<function tokenize at 0x7f2d86167160>, split_sents=False, keep_tok_func=functools.partial(<function keep_tok at 0x7f2d86167280>), parse_tok_func=functools.partial(<function parse_tok at 0x7f2d861671f0>))]



Now we loop through rows in the doctable and for each iteration parse the text and insert it back into the table using `.update()`. We use the `ParsePipeline` method `.parsemany()` to parse paragraphs from each document in parallel. This is much faster.


```python
docs = db.select()
for doc in tqdm(docs):
    doc.parsed = parser.parsemany(doc.text[:1000].split('\n\n'), workers=8) # parse paragraphs in parallel
    db.update_dataclass(doc, verbose=False)
```

      0%|          | 0/51 [00:00<?, ?it/s]

    DocTable: SELECT _documents_.id, _documents_.year, _documents_.president, _documents_.party, _documents_.text, _documents_.parsed 
    FROM _documents_


    100%|██████████| 51/51 [00:04<00:00, 11.42it/s]


See the 'parsed' column in the dataframe below to view the paragraphs.


```python
db.select_df(limit=3)
```

    DocTable: SELECT _documents_.id, _documents_.year, _documents_.president, _documents_.party, _documents_.text, _documents_.parsed 
    FROM _documents_
     LIMIT ? OFFSET ?





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
      <th>president</th>
      <th>party</th>
      <th>text</th>
      <th>parsed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>1987</td>
      <td>Reagan</td>
      <td>R</td>
      <td>I. An American Perspective \n\nIn the early da...</td>
      <td>[[I., An, American, Perspective], [in, the, ea...</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>1993</td>
      <td>H.W. Bush</td>
      <td>R</td>
      <td>Preface \n\nAmerican Leadership for Peaceful C...</td>
      <td>[[preface], [American, leadership, for, peacef...</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2002</td>
      <td>W. Bush</td>
      <td>R</td>
      <td>The great struggles of the twentieth century b...</td>
      <td>[[the, great, struggles, of, the, twentieth, c...</td>
    </tr>
  </tbody>
</table>
</div>



And here we show a few tokenized paragraphs.


```python
paragraphs = db.select_first('parsed')
for par in paragraphs[:3]:
    print(par, '\n')
```

    DocTable: SELECT _documents_.parsed 
    FROM _documents_
     LIMIT ? OFFSET ?
    ['I.', 'An', 'American', 'Perspective'] 
    
    ['in', 'the', 'early', 'days', 'of', 'this', 'administration', 'we', 'laid', 'the', 'foundation', 'for', 'a', 'more', 'constructive', 'and', 'positive', 'American', 'role', 'in', 'world', 'affairs', 'by', 'clarifying', 'the', 'essential', 'elements', 'of', 'U.S.', 'foreign', 'and', 'defense', 'policy', '.'] 
    
    ['over', 'the', 'intervening', 'years', ',', 'we', 'have', 'looked', 'objectively', 'at', 'our', 'policies', 'and', 'performance', 'on', 'the', 'world', 'scene', 'to', 'ensure', 'they', 'reflect', 'the', 'dynamics', 'of', 'a', 'complex', 'and', 'ever', '-', 'changing', 'world', '.', 'where', 'course', 'adjustments', 'have', 'been', 'required', ',', 'i', 'have', 'directed', 'changes', '.', 'but', 'we', 'have', 'not', 'veered', 'and', 'will', 'not', 'veer', 'from', 'the', 'broad', 'aims', 'that', 'guide', 'America', "'s", 'leadership', 'role', 'in', 'today', "'s", 'world', ':'] 
    

