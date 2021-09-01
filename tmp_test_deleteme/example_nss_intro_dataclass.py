#!/usr/bin/env python
# coding: utf-8

# # Example 1: US National Security Strategy Document Corpus
# In this example, I'll show how to create a database for document + metadata storage using the `DocTable` class, and a parser class using a `ParsePipeline`. We will store the metadata you see below with the raw text and parsed tokens in the same DocTable.

# In[1]:


import sys
sys.path.append('..')
import doctable
import spacy
from tqdm import tqdm
import pandas as pd
import os
from pprint import pprint
import urllib.request # used for downloading nss docs


# ## Introduction to NSS Corpus
# This dataset is the plain text version of the US National Security Strategy documents. During the parsing process, all plain text files will be downloaded from my [github project hosting the nss docs](https://github.com/devincornell/nssdocs). I compiled the metadata you see below from [a page hosted by the historical dept of the secretary's office](https://history.defense.gov/Historical-Sources/National-Security-Strategy/). In short, each US President must release at least one NSS per term, with some (namely Clinton) producing more.
# 
# Here I've created the function `download_nss` to download the text data from my nssdocs github repository, and the python dictionary `nss_metadata` to store information about each document to be stored in the database.

# In[2]:


def download_nss(year):
    ''' Simple helper function for downloading texts from my nssdocs repo.'''
    baseurl = 'https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/{}.txt'
    url = baseurl.format(year)
    text = urllib.request.urlopen(url).read().decode('utf-8')
    return text


# In[3]:


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


# In[4]:


# downloader example: first 100 characters of 1993 NSS document
text = download_nss(1993)
text[:100]


# ## 1. Create a DocTable Schema
# The `DocTable` class is often used by subclassing. Our `NSSDocs` class inherits from `DocTable` and will store connection and schema information. Because the default constructor checks for statically define member variables `tabname` and `schema` (as well as others), we can simply add them to the class definition. 
# 
# In this example, we create the 'id' column as a unique index, the 'year', 'president', and 'party' columns for storing the metadata we defined above in `nss_metadata`, and columns for raw and parse text. See the [schema guide](examples/doctable_schema.html) for examples of the full range of column types.

# In[5]:


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
        
    _constraints_ = [('check', 'party in ("R", "D")')]
    _indices_ = {'ind_yr': ('year', dict(unique=True))}


# We can then create a connection to a database by instantiating the `NSSDocs` class. Since the `fname` parameter was not provided, this doctable exists only in memory using sqlite (uses special sqlite name ":memory:"). We will use this for these examples.
# 
# We can check the sqlite table schema using `.schema_table()`. You can see that the 'pickle' datatype we chose above is represented as a BLOB column. This is because DocTable, using SQLAlchemy core, creates an interface on top of sqlite to handle the data conversion. You can view the number of documents using `.count()` or by viewing the db instance as a string (in this case with print function).

# In[6]:


# printing the DocTable object itself shows how many entries there are
db = doctable.DocTable(schema=NSSDoc, target=':memory:', verbose=True)
print(db.count())
print(db)
db.schema_table()


# ## 2. Insert Data Into the Table

# Now let's download and store the text into the database. Each loop downloads a text document and inserts it into the doctable, and we use the `.insert()` method to insert a single row at a time. The row to be inserted is represented as a dictionary, and any missing column information is left as NULL. The `ifnotunique` argument is set to false because if we were to re-run this code, it needs to replace the existing document of the same year. Recall that in the schema we placed a unique constraint on the year column.

# In[7]:


for year, docmeta in tqdm(nss_metadata.items()):
    text = download_nss(year)
    db.insert(NSSDoc(
        year=year, 
        party=docmeta['party'], 
        president=docmeta['president'], 
        text=text
    ), ifnotunique='replace', verbose=False)
db.head()


# ## 3. Query Table Data
# Now that we have inserted the NSS documents into the table, there are a few ways we can query the data. To select the first entry of the table use `.select_first()`. This method returns a simple `sqlalchemy.RowProxy` object which can be accessed like a dictionary or like a tuple.

# In[8]:


row = db.select_first()
#print(row)
print(row['president'])


# To select more than one row, use the `.select()` method. If you'd only like to return the first few rows, you can use the `limit` argument.

# In[9]:


rows = db.select(limit=2)
print(rows[0]['year'])
print(rows[1]['year'])


# We can also select only a few columns.

# In[10]:


db.select(['year', 'president'], limit=3)


# For convenience, we can also use the `.select_df()` method to return directly as a pandas dataframe.

# In[11]:


# use select_df to show a couple rows of our database
db.select_df(limit=2)


# ## 4. Create a Parser for Tokenization
# Now that the text is in the doctable, we can extract it using `.select()`, parse it, and store the parsed text back into the table using `.update()`.
# 
# Now we create a parser using `ParsePipeline` and a list of functions to apply to the text sequentially. The `Comp` function returns a [doctable parse function](ref/doctable.parse.html) with additional keyword arguments. For instance, the following two expressions would be the same.
# ```
# doctable.component('keep_tok', keep_punct=True) # is equivalent to
# lambda x: doctable.parse.parse_tok_func(x, keep_punct=True)
# ```
# Note in this example that the 'tokenize' function takes two function arguments `keep_tok_func` and `parse_tok_func` which are also specified using the `.Comp()` function. The available pipeline components are listed in the [parse function documentation](ref/doctable.parse.html).

# In[12]:


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


# Now we loop through rows in the doctable and for each iteration parse the text and insert it back into the table using `.update()`. We use the `ParsePipeline` method `.parsemany()` to parse paragraphs from each document in parallel. This is much faster.

# In[13]:


docs = db.select()
for doc in tqdm(docs):
    doc.parsed = parser.parsemany(doc.text[:1000].split('\n\n'), workers=8) # parse paragraphs in parallel
    db.update_dataclass(doc, verbose=False)


# See the 'parsed' column in the dataframe below to view the paragraphs.

# In[14]:


db.select_df(limit=3)


# And here we show a few tokenized paragraphs.

# In[15]:


paragraphs = db.select_first('parsed')
for par in paragraphs[:3]:
    print(par, '\n')

