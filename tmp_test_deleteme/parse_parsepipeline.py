#!/usr/bin/env python
# coding: utf-8

# # `ParsePipeline` Basics
# Here I demonstrate the basics of parsing text using [Spacy](https://spacy.io/) + doctable to tokenize text. Spacy does most of the heavy-lifting here to actually parse the document, and doctable methods handle the conversion from the Spacy Document object to a sequence of string tokens (words).

# In[1]:


from IPython import get_ipython
import sys
sys.path.append('..')
import doctable


# In[2]:


ex_texts = [
    'I am pretty bored today. I have been stuck in quarantine for more than two months!',
    'We are all waiting on Dr. Fauci to let us know when to return from quarantine.',
    'On the bright side, I have more time to talk to my distant friends over video chat.',
    'But still, I wish I could travel, go to bars, and go out to eat mrore often!',
    'Here we show an example URL: https://devincornell.github.io/doctable/',
    'And also one with <b><i>xml tags</i></b>.',
]


# ## 1. Build a `ParsePipeline` for Tokenization
# 
# `ParsePipeline` makes it easy to define a processing pipeline as a list of functions (called components) to apply sequentially to each document in your corpus. You can use the `.parsemany()` method to run the pipeline on documents in paralel, or simply use the `.parse()` method to parse a single document.
# 
# Our most basic pipeline uses a lambda function to split each text document by whitespace.

# In[3]:


parser_split = doctable.ParsePipeline([
    lambda text: text.split(),
])


# We then use the `.parse()` method to apply the pipeline to a single document.

# In[4]:


parsed_text = parser_split.parse(ex_texts[0])
print(parsed_text[:7])


# We can also use the `.parsemany()` method to parse all of our texts at once. Use the `workers` parameter to specify the number of processes to use if you want to use parallelization.

# In[5]:


parsed_texts = parser_split.parsemany(ex_texts, workers=2) # processes in parallel
for text in parsed_texts:
    print(text[:7])


# ## 2. Use doctable Parsing Components
# doctable has some built-in methods for pre- and post-processing Spacy documents. This list includes all functions in the [doctable.parse](ref/doctable.parse.html) namespace, and you can access them using the `doctable.Comp` function.

# In[6]:


print(doctable.components)


# In[7]:


preproc = doctable.Comp('preprocess', replace_url='_URL_', replace_xml='')
print(ex_texts[4])
preproc(ex_texts[4])


# Now we show a pipeline that uses the doctable `preprocess` method to remove xml tags and urls, the [Spacy nlp model](https://spacy.io/usage/spacy-101) to parse the document, and the built-in `tokenize` method to convert the spacy doc object to a list of tokens. 

# In[8]:


from doctable import Comp
import spacy
nlp = spacy.load('en_core_web_sm')

parser_tok = doctable.ParsePipeline([
    Comp('preprocess', replace_xml='', replace_url='XXURLXX'),
    nlp,
    Comp('tokenize', split_sents=False),
])

docs = parser_tok.parsemany(ex_texts)
for doc in docs:
    print(doc[:10])


# ## 3. More Complicated Pipelines
# 
# Now we show a more complicated mode. The function `tokenize` also takes two additional methods: `keep_tok_func` determines whether a Spacy token should be included in the final document, and the `parse_tok_func` determines how the spacy token objects should be converted to strings. We access the doctable `keep_tok` and `parse_tok` methods using the same `Comp` function to create nested parameter lists.

# In[9]:


parser_full = doctable.ParsePipeline([
    
    # preprocess to remove xml tags and replace URLs (doctable.parse.preprocess)
    Comp('preprocess', replace_xml='', replace_url='XXURLXX'),
    nlp, # spacy nlp parser object
    
    # merge spacy multi-word named entities (doctable.parse.merge_tok_spans)
    Comp('merge_tok_spans', merge_ents=True, merge_noun_chunks=False),
    
    # tokenize document
    Comp('tokenize', **{
        'split_sents': False,
        
        # choose tokens to keep (doctable.parse.keep_tok)
        'keep_tok_func': Comp('keep_tok', **{
            'keep_whitespace': False, # don't keep whitespace
            'keep_punct': True, # keep punctuation and stopwords
            'keep_stop': True,
        }),
        
        # choose how to convert Spacy token t text (doctable.parse.parse_tok)
        'parse_tok_func': Comp('parse_tok', **{
            'format_ents': True,
            'lemmatize': False,
            'num_replacement': 'NUM',
            'ent_convert': lambda e: e.text.upper(), # function to capitalize named entities
        })
    })
])
len(parser_full.components)


# In[10]:


get_ipython().run_line_magic('time', 'parsed_docs = parser_full.parsemany(ex_texts)')
for tokens in parsed_docs:
    print(tokens[:10])


# These are the fundamentals of building `ParsePipeline`s in doctable. While these tools are totally optional, I believe they make it easier to structure your code for text analysis applications.
