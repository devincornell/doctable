#!/usr/bin/env python
# coding: utf-8

# # DocParser Tokenization
# 

# In[38]:


import sys
sys.path.append('..')
import doctable as dt
from spacy import displacy
import spacy
nlp = spacy.load('en_core_web_sm')
from spacy.matcher import Matcher


# DocParser is built specifically to convert spacy doc objects to token lists or simple parsetree objects which are convenient to store in a doctable. As such, we begin by creating a spacy doc object.

# In[2]:


exstr = 'James will paint the house for $20 (twenty dollars). He is a rule-breaker'
doc = nlp(exstr)
doc


# ## Document Tokenizing
# 
# Typically you will want to parse at the Spacy doc aobject. The `.tokenize_doc()` method includes common functionality for tokenizing your documents. Arguments to this function present a series of decisions that need to be made for every tokenization process. There are two 

# In[4]:


# the most basic version performs tokenizing with all default settings
print(dt.DocParser.tokenize_doc(doc))


# In[5]:


# split into sentences (list of lists)
print(dt.DocParser.tokenize_doc(doc, split_sents=True))


# In[6]:


print(dt.DocParser.tokenize_doc(doc, merge_ents=True))
doc = nlp(exstr) # reverts doc back to original because adding the match (called in .tokenize_doc()) modified it


# In[7]:


print(dt.DocParser.tokenize_doc(doc, merge_noun_chunks=True))
doc = nlp(exstr) # reverts doc back to original because adding the match (called in .tokenize_doc()) modified it


# ### Choose to include tokens
# You may not want to include all tokens, depending on spacy token information. For this case, we use the `.use_tok()` method which includes some built-in arguments to do some boilerplate steps. Again see the [full documentaiton](https://devincornell.github.io/doctable/ref/doctable.DocParser.html) to see all arguments and defaults.
# The function simply returns a boolean True/False value given a spacy token, but can be passed to `.tokenize_doc()` for added flexibility.
# 
# It is most easily used by overriding parameters through a lambda function.

# In[8]:


# first try a custom function keeps only non-numbers
use_tok_nobreaker = lambda tok: not tok.like_num
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok_nobreaker))


# In[9]:


# now, you can override the .use_tok() to take care of some simple stuff
use_tok_nostop = lambda tok: dt.DocParser.use_tok(tok, filter_stop=True)
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok_nostop))


# In[40]:


# remove digits
use_tok_nodigit = lambda tok: dt.DocParser.use_tok(tok, filter_digit=True)
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok_nodigit))


# In[11]:


# remove numbers (see it removed both "20" and "Twenty")
use_tok_nonum = lambda tok: dt.DocParser.use_tok(tok, filter_num=True)
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok_nonum))


# In[12]:


# here it thought 'James' was an organization. Use the filter_ent_types arg to remove specific ent types
use_tok_nonames = lambda tok: dt.DocParser.use_tok(tok, filter_ent_types=['ORG'])
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok_nonames))


# In[13]:


# remove all entities using the filter_all_ents argument
use_tok_nonents = lambda tok: dt.DocParser.use_tok(tok, filter_all_ents=True)
print(dt.DocParser.tokenize_doc(doc, use_tok_func=use_tok_nonents))


# In[14]:


# you can also add to the use_tok method using a custom function
def custom_use_tok(tok):
    use = dt.DocParser.use_tok(tok, filter_num=True)
    return use and tok.pos_ != 'VERB' # here removes all verbs (including "paint")
print(dt.DocParser.tokenize_doc(doc, use_tok_func=custom_use_tok))


# ### Choose how to parse tokens
# Conversion from a spacy token to a string can happen a number of different ways. The `.parse_tok()` method provides a number of features for this task, or a custom function can be provided.

# In[15]:


#parse_tok(tok, replace_num=None, replace_digit=None, lemmatize=False, normal_convert=None, format_ents=True, ent_convert=None)


# In[16]:


# a custom function will simply return the original text using the tok.text property
parse_tok = lambda tok: tok.text
print(dt.DocParser.tokenize_doc(doc, parse_tok_func=parse_tok))


# In[17]:


# using .parse_tok(), first try replacing numbers with "__NUM__"
parse_tok = lambda tok: dt.DocParser.parse_tok(tok, replace_num='__NUM__')
print(dt.DocParser.tokenize_doc(doc, parse_tok_func=parse_tok))


# In[18]:


# now lemmatize
parse_tok = lambda tok: dt.DocParser.parse_tok(tok, lemmatize=True)
print(dt.DocParser.tokenize_doc(doc, parse_tok_func=parse_tok))


# In[41]:


# format_ents is one of the most useful features. 
# It will standardize ents by converting all consecutive whitespace to 
# spaces and then capitalize the first letter. This is the default setting, but it can be turned off.
parse_tok = lambda tok: dt.DocParser.parse_tok(tok, format_ents=True)
print(dt.DocParser.tokenize_doc(doc, parse_tok_func=parse_tok))


# ### Merging N-Grams
# DocParser offers two convenient ways to work with n-grams: (1) using the spacy matcher and (2) using the post-processed multi-token matcher. The first method is applied after normal spacy processing is finished. It involves passing a tuple of ngrams as tuples to apply after all parsing has completed. The good thing about this approach is that it doesn't require much code. The unfortunate thing is that it can only access the tokens after normal parsing. If you would like to merge tokens with hyphens between them or currency symbols to their numbers, you should use the pre-processing method.
# 
# The pre-processing spacy.Matcher functionality is used to create ngrams which access certain underlying spacy components like IS_DIGIT etc. See [Spacy Matcher documention for more details](https://spacy.io/usage/rule-based-matching). The basic workflow is to create a matcher object, add patterns, and then pass matcher to .tokenize_doc(). Note that since the doc object itself is modified, python must be restarted to revert back to other tokenization method.

# In[20]:


# post-parsing ngram merging
ngrams = (
    ('the', 'house'),
    ('rule', '-', 'breaker'),
    ('he', 'is', 'a'),
)
# by default 
print(dt.DocParser.tokenize_doc(doc, ngrams=ngrams))
print()
print(dt.DocParser.tokenize_doc(doc, ngrams=ngrams, ngram_sep='_')) # specify ngram_sep


# In[21]:


# spacy matcher object (will be passed to docparser)
matcher = Matcher(nlp.vocab)

# matches currency numbers
pattern = [{'TEXT':'$'},{'IS_DIGIT':True}]
matcher.add('currency', None, pattern)

# matches the phrase "he will" or "He Will" or "HE WILL"
pattern2 = [{'LOWER':'he'},{'LOWER':'will'}]
matcher.add('he_will', None, pattern2)

# matches hyphens
pattern3 = [{'IS_SPACE':False},{'TEXT':'-'},{'IS_SPACE':False}]
matcher.add('he_will', None, pattern3)

print([tok for tok in dt.DocParser.tokenize_doc(doc, spacy_ngram_matcher=matcher)])
doc = nlp(exstr) # reverts doc back to original because adding the match (called in .tokenize_doc()) modified it

