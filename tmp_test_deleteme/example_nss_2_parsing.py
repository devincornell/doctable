#!/usr/bin/env python
# coding: utf-8

# # Vignette 2: Storing Document Text
# In this example, I'll show how to create a database for document text + metadata storage using the `DocTable` class, and a parser class using a `ParsePipeline`. We will store the metadata you see below with the raw text and parsed tokens in the same DocTable.
# 
# These are the vignettes I have created:
# 
# + [1: Storing Document Metadata](example_nss_1_intro.html)
# 
# + [2: Storing Document Text](example_nss_2_parsing.html)
# 
# + [3: Storing Parsed Documents](example_nss_3_parsetrees.html)

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

# automatically clean up temp folder after python ends
tmpfolder = doctable.TempFolder('tmp')


# ## Introduction to NSS Corpus
# This dataset is the plain text version of the US National Security Strategy documents. During the parsing process, all plain text files will be downloaded from my [github project hosting the nss docs](https://github.com/devincornell/nssdocs). I compiled the metadata you see below from [a page hosted by the historical dept of the secretary's office](https://history.defense.gov/Historical-Sources/National-Security-Strategy/). In short, each US President must release at least one NSS per term, with some (namely Clinton) producing more.
# 
# I've defined the document metadata as `nss_metadata`, which contains the year (which I used to make the url), the president name, and the political party they belong to. We will later use `download_nss()` to actually download the text and store it into the database.

# In[2]:


def download_nss(year):
    ''' Simple helper function for downloading texts from my nssdocs repo.'''
    baseurl = 'https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/{}.txt'
    url = baseurl.format(year)
    text = urllib.request.urlopen(url).read().decode('utf-8')
    return text


# In[3]:


document_metadata = [
    {'year': 2000, 'party': 'D', 'president': 'Clinton'},
    {'year': 2002, 'party': 'R', 'president': 'W. Bush'}, 
    {'year': 2006, 'party': 'R', 'president': 'W. Bush'}, 
    {'year': 2010, 'party': 'D', 'president': 'Obama'}, 
    {'year': 2015, 'party': 'D', 'president': 'Obama'}, 
    {'year': 2017, 'party': 'R', 'president': 'Trump'}, 
]


# In[4]:


# downloader example: first 100 characters of 1993 NSS document
text = download_nss(1993)
text[:100]


# ## 1. Create a Table Schema
# 
# The first step will be to define a database schema that is appropriate for the data in `document_metadata`. We define an `NSSDoc` class to represent a single document. The `doctable.schema` decorator will convert the row objects into [`dataclasses`](https://realpython.com/python-data-classes/) with [slots](https://docs.python.org/3/reference/datamodel.html#slots) enabled, and inherit from doctable.DocTableRow to add some additional functionality. The type hints associated with each variable will be used in the schema definition for the new tables, and arguments to `doctable.Col` will mostly be passed to `dataclasses.field` (see [docs](https://doctable.org/ref/doctable/schemas/field_columns.html#Col) for more detail), so all dataclass functionality is maintained.
# 
# See the [schema guide](examples/doctable_schema.html) for examples of the full range of column types.

# In[5]:


from typing import Any # import generic type hint

# to be used as a database row representing a single NSS document
@doctable.schema
class NSSDoc:
    __slots__ = [] # include so that doctable.schema can create a slot class
    
    id: int = doctable.IDCol() # this is an alias for doctable.Col(primary_key=True, autoincrement=True)
    year: int =  doctable.Col()
    party: str = doctable.Col()
    president: str = doctable.Col()
    text: str = doctable.Col()
    tokens: Any = doctable.Col() # this will be used as a binary type that stores pickled data
        
    @property
    def num_tokens(self):
        return len(self.tokens)
        
    def paragraphs(self):
        return self.text.split('\n\n')


# ## 2. Define a Custom DocTable
# 
# Now we define a class called `NSSDocTable` to represent the database table. This table must inherit from `DocTable` and will store connection and schema information.
# The `DocTable` class is often used by subclassing. Our `NSSDocs` class inherits from `DocTable` and will store connection and schema information. Because the default constructor checks for statically define member variables `tabname` and `schema` (as well as others), we can simply add them to the class definition. 
# 
# We also can use this definition to create indices and constraints using the `_indices_` and `_constraints_` member variables. The indices are provided as name->columns pairs, and the constraints are tuples of the form `(constraint_type, constraint_details)`. In this case, we limit the values for `check` to R or D.

# In[6]:


class NSSDocTable(doctable.DocTable):
    _tabname_ = 'nss_documents'
    _schema_ = NSSDoc
    _indices_ = (
        doctable.Index('party_index', 'party'),
    )
    _constraints_ = (
        doctable.Constraint('check', 'party in ("R", "D")'),
    )


# We can then create a connection to a database by instantiating the `NSSDocTable` class. We used `target=':memory:'` to indicate that the sqlite table should be created in-memory.

# In[7]:


# printing the DocTable object itself shows how many entries there are
nss_table = NSSDocTable(target=':memory:')
print(nss_table.count())
print(nss_table)
nss_table.schema_table()


# ## 2. Insert Data Into the Table

# Now let's download and store the text into the database. Each loop downloads a text document and inserts it into the doctable, and we use the `.insert()` method to insert a single row at a time. The row to be inserted is represented as a dictionary, and any missing column information is left as NULL. The `ifnotunique` argument is set to false because if we were to re-run this code, it needs to replace the existing document of the same year. Recall that in the schema we placed a unique constraint on the year column.

# In[8]:


for docmeta in tqdm(document_metadata):
    text = download_nss(docmeta['year'])
    nss_table.insert({**docmeta, **{'text': text}}, ifnotunique='replace')
nss_table.head()


# ## 3. Query Table Data
# Now that we have inserted the NSS documents into the table, there are a few ways we can query the data. To select the first entry of the table use `.select_first()`. This method returns a simple `sqlalchemy.RowProxy` object which can be accessed like a dictionary or like a tuple.

# In[9]:


row = nss_table.select_first(['id', 'year', 'party', 'president'])
print(row)
print(row['president'])


# To select more than one row, use the `.select()` method. If you'd only like to return the first few rows, you can use the `limit` argument.

# In[10]:


rows = nss_table.select(limit=2)
print(rows[0]['year'])
print(rows[1]['year'])


# We can also select only a few columns.

# In[11]:


nss_table.select(['year', 'president'], limit=3)


# For convenience, we can also use the `.select_df()` method to return directly as a pandas dataframe.

# In[12]:


# use select_df to show a couple rows of our database
nss_table.select_df(limit=2)


# And access the `.paragraphs()` method we defined in `NSSDoc`.

# In[13]:


for row in nss_table.select(limit=3):
    print(f"{row['president']} ({row['year']}): num_paragraphs={len(row.paragraphs())}")


# ## 4. Create a Parser for Tokenization
# Now that the text is in the doctable, we can extract it using `.select()`, parse it, and store the parsed text back into the table using `.update()`.
# 
# Now we create a parser using `ParsePipeline` and a list of functions to apply to the text sequentially. The `Comp` function returns a [doctable parse function](ref/doctable.parse.html) with additional keyword arguments. For instance, the following two expressions would be the same.
# ```
# doctable.Comp('keep_tok', keep_punct=True) # is equivalent to
# lambda x: doctable.parse.parse_tok_func(x, keep_punct=True)
# ```
# Note in this example that the 'tokenize' function takes two function arguments: `keep_tok_func` and `parse_tok_func`, which are also specified using the `.Comp()` function. The available pipeline components are listed in the [parse function documentation](ref/doctable.parse.html).

# In[14]:


# add pipeline components
parser = doctable.ParsePipeline([
    spacy.load('en_core_web_sm'), # load a spacy parser as first step in pipeline
    doctable.Comp('tokenize', **{
        'split_sents': False,
        'keep_tok_func': doctable.Comp('keep_tok'),
        'parse_tok_func': doctable.Comp('parse_tok'),
    })
])

parser.components


# Now we loop through rows in the doctable and for each iteration parse the text and insert it back into the table using `.update()`. We use the `ParsePipeline` method `.parsemany()` to parse paragraphs from each document in parallel.

# In[15]:


for doc in tqdm(nss_table.select(['id','year','text'])):
    paragraphs = parser.parsemany(doc.text.split('\n\n'), workers=30) # parse paragraphs in parallel
    nss_table.update({'tokens': [t for p in paragraphs for t in p]}, where=nss_table['id']==doc['id'])


# In[16]:


nss_table.select_df(limit=3)


# In[17]:


for doc in nss_table.select():
    print(f"{doc.president} ({doc.year}): {len(doc.tokens)} tokens.")


# And that is all for this vignette! See the list of vignettes at the top of this page for more examples.
