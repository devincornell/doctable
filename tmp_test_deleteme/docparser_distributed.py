#!/usr/bin/env python
# coding: utf-8

# # Distributed Parsing
# These examples will show how to use the DocParser class to make a parallelized parsing pipeline. Most of these features are in two methods:
# 
# 
# * **`.distribute_parse()`**: A text processing-specific method that will distribute texts among processors, apply a supplied preprocssing function, process using spacy's nlp.pipe(), and then parse to a non-spacy object using a supplied function. If a dt_inst keyword argument is defined, your supplied function may additionally insert the parsed result into the DocTable directly from the parsing process.
# 
# * **`.distribute_process()`**: A more general function that allows you to distribute parsing of any element list and then if supplied with dt_inst can insert into the DocTable. This is ideal for cases where you do not want to store all texts into memory at once (as `distribute_parse()` requires, and could instead supply a list of filenames that then could be read, preprocessed, postprocessed, and inserted into the database all within the distributed processes.
# 
# * **`.distribute_chunks()`**: A function that creates processes and allows you to provide a function which operates on a chunk of the provided elements.

# In[1]:


from spacy import displacy
import spacy
nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher
from pprint import pprint
import sys
sys.path.append('..')
import doctable as dt


# In[2]:


texts_small = ['The hat is red. And so are you.\n\nWhatever, they said. Whatever indeed.', 
               'But why is the hat blue?\n\nAre you colorblind? See the answer here: http://google.com']


# ## `.distribute_parse()`

# In[3]:


# this is the straightforward mode where it tokenizes each doc in parallel
# using default document preprocessing and parsing
parsed = dt.DocParser.distribute_parse(texts_small, nlp)
print(parsed)


# In[4]:


# use paragraph_sep to maintain paragraph information
parsed = dt.DocParser.distribute_parse(texts_small, nlp, paragraph_sep='\n\n')
print(parsed)


# In[5]:


# this shows an exmple where it will customize every element of the process
def preprocess(text): return dt.DocParser.preprocess(text, replace_url='')
def use_token_overload(tok): return dt.DocParser.use_tok(tok, filter_stop=False, filter_punct=False)
def parse_token_overload(tok): return dt.DocParser.parse_tok(tok, lemmatize=False)
def parsefunc(doc): return dt.DocParser.tokenize_doc(doc, use_tok_func=use_token_overload, parse_tok_func=parse_token_overload, split_sents=True)
parsed = dt.DocParser.distribute_parse(texts_small, nlp, parsefunc=parsefunc, preprocessfunc=preprocess)
pprint(parsed)


# ### Parse and insert into database
# The best part about all of these methods is that you can place them into a doctable directly, rather than returning them.

# In[6]:


def parse_insert(doc, db):
    toks = dt.DocParser.tokenize_doc(doc)
    db.insert({'tokens':toks})
db = dt.DocTable(schema=[('pickle','tokens')], fname='t12.db')
db.delete() # empty if it had some rows
dt.DocParser.distribute_parse(texts_small, nlp, dt_inst=db, parsefunc=parse_insert)
print(db.select_df())


# ### With parsetrees or arbitrary objects
# The fact that you can pass custom parsers means you can also use parsetrees or any other custom document representation.

# In[7]:


def preprocess(text): return dt.DocParser.preprocess(text, replace_url='')
def parse_token_overload(tok): return dt.DocParser.parse_tok(tok, lemmatize=False)
def parsefunc(doc): return dt.DocParser.get_parsetrees(doc, parse_tok_func=parse_token_overload)
parsed = dt.DocParser.distribute_parse(texts_small, nlp, parsefunc=parsefunc, preprocessfunc=preprocess)
pprint(parsed)


# In[8]:


def pf(doc):
    return len(doc)
dt.DocParser.distribute_parse(texts_small, nlp, parsefunc=pf)


# In[9]:


def pf(doc):
    return len(doc)
dt.DocParser.distribute_parse(texts_small, nlp, parsefunc=pf, paragraph_sep='\n\n')

