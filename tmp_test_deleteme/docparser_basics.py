#!/usr/bin/env python
# coding: utf-8

# # DocParser Class
# This example gives an overview of DocParser functionality. See [reference docs for more detail](https://devincornell.github.io/doctable/ref/doctable.DocParser.html). The class includes only classmethods and staticmethods, so it is meant to be inhereted rather than instantiated.
# 
# The DocParser class currently facilitates conversion from spacy doc objects to one of two object types:
# 1. **Token lists**: The `.tokenize_doc()` method produces sequences of token strings used for input into algorithms like word2vec, topic modeling, co-occurrence analyses, etc. These require no doctable-specific functionality to manipulate. To accomplish this, it also draws on `.parse_tok()` to specify rules for converting spacy token objects to strings and `.use_tok()` to decide whether or not to include a token.
# 2. **Parsetrees**: The `get_parsetrees()` method produces objects used for grammatical structure analysis. Generally contains token information along with gramattical relationships observed in the original sentences. By default relies on the `.parse_tok()` method to convert token objects to string representations. DocParser can convert these to nested dictionaries or also provides a built-in `ParseTree` class for working with them.

# In[1]:


import sys
sys.path.append('..')
import doctable as dt
from spacy import displacy
import spacy
nlp = spacy.load('en_core_web_sm')


# In[2]:


exstr = 'James will paint the house for $20 (twenty dollars). He is a rule-breaker'
doc = nlp(exstr)
doc


# ## Preprocessing
# The first step before using spacy to parse a document is to preprocess, which usually means removing artifacts. The `.preprocess()` method has features for replacing urls, replacing xml tags, and removing digits.

# In[3]:


advstr = 'James said he will paint the house red for $20 (twenty dollars). He is such a <i>rule-breaker</i>: http://rulebreaking.com'
dt.DocParser.preprocess(advstr, replace_url='URL', replace_xml='', replace_digits='DIG')


# Normally after preprocessing you will then feed into the spacy parser.

# ## Tokenization
# Many text analysis applications begin with converting raw text into sequences of tokens. The `.tokenize_doc()`, `.use_tok()`, and `.parse_tok()` methods are convenient tools to assist with this task.

# In[4]:


# basic doc tokenizer works like this
print(dt.DocParser.tokenize_doc(doc))


# In[5]:


# and there are a number of options when using this method
print(dt.DocParser.tokenize_doc(doc, split_sents=True, merge_ents=True, merge_noun_chunks=True))


# In[6]:


# you can override functionality to decide to keep the token and to convert tok object to str
use_tok = lambda tok: not tok.like_num
parse_tok = lambda tok: tok.lower_
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok, parse_tok_func=parse_tok))


# In[7]:


# or use DocParser .use_tok() and .parse_tok() methods for additional features.
# this filters out stopwords and converts all number quantities to __NUM__
use_tok = lambda tok: dt.DocParser.use_tok(tok, filter_stop=True)
parse_tok = lambda tok: dt.DocParser.parse_tok(tok, format_ents=True, replace_num='__NUM__')
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok, parse_tok_func=parse_tok))


# ## Parsetree Extraction
# In cases where you want to keep information about gramattical structure in your parsed document, use the `.get_parsetrees()` method.

# In[8]:


# extracts a parsetree for each sentence in the document
print(dt.DocParser.get_parsetrees(doc))


# In[19]:


# by default this works like .tokenize_doc() except that it doesn't remove toks
# it includes a lot of other information as well
# it will include .pos and .ent if they were available in spacy parsing
s1, s2 = dt.DocParser.get_parsetrees(doc)
print([t.tok for t in s1])
print([t.dep for t in s1])
print([t.tag for t in s1])
print([t.pos for t in s1])
print([t.ent for t in s1])


# In[12]:


# much like .tokenize_doc(), you can specify the parse_token functionality 
#     that will be applied to the .tok property
parse_tok = lambda tok: tok.text.upper()
s1, s2 = dt.DocParser.get_parsetrees(doc, parse_tok_func=parse_tok)
print(s1.toks)


# In[20]:


# to attach additional info to parsetree tokens, use info_func_map
infomap = {'is_stop':lambda tok: tok.is_stop, 'like_num': lambda tok: tok.like_num}
s1, s2 = dt.DocParser.get_parsetrees(doc, info_func_map=infomap)
print(s1.toks)
print([t.info['like_num'] for t in s1])


# In[28]:


# we can convert to dict to see tree structure
s1, s2 = dt.DocParser.get_parsetrees(doc)
s1.asdict()


# #### Working with ParseTree objects
# ParseTree objects can be parsed either iteratively (as we showed earlier), or recursively. The `.bubble_accum()` and `.bubble_reduce()` methods are convenient ways of using recursive functions on parsetrees. The `.root` property is also a useful way to write your own recursive functions on the data.

# In[31]:


# .bubble_accum() 
def get_ents(pnode):
    if pnode.ent != '':
        return [pnode]
    else:
        return []
s1, s2 = dt.DocParser.get_parsetrees(doc)
s1.bubble_accum(get_ents)


# In[34]:


# .bubble_reduce() will aggregate data as it performs a DFS
def f(pn,ct):
    return ct + 1
s1, s2 = dt.DocParser.get_parsetrees(doc)
s1.bubble_reduce(f, 0)


# In[35]:


# or write your own recursive functions using s1.root to 
#     access the root node of the tree
def printnodes(pnode):
    print(pnode.tok, pnode.dep, pnode.pos)
    for child in pnode:
        printnodes(child)
s1, s2 = dt.DocParser.get_parsetrees(doc)
printnodes(s1.root)

