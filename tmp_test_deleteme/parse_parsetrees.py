#!/usr/bin/env python
# coding: utf-8

# # Working with doctable Parsetrees
# Here I'll show you how to extract and use parsetrees in your doctable using Spacy + doctable. The motivation is that parsetree information in raw Spacy Document objects are very large and not suitable for storage when using large corpora. We solve this by simply converting the Spacy Document object to a tree data structure built from python lists and dictionaries, and use the `ParseTree` object to serialize, de-serialize, and interact with the tree structure.
# 
# We use this feature using the `get_parsetrees` pipeline component after the spacy parser. [Check the docs](ref/doctable.parse.html) to learn more about this function. You can see more examples of creating parse pipelines in our [overview examples](examples/parse_basics.html).

# In[1]:


import spacy
nlp = spacy.load('en_core_web_sm')
import pandas as pd
import sys
sys.path.append('..')
import doctable


# First we define some example text docuemnts, Star Wars themed.

# In[2]:


text = 'Help me Obi-Wan Kenobi. You’re my only hope. '     'I find your lack of faith disturbing. '     'Do, or do not - there is no try. '
text


# ## Creating `ParseTreeDoc` Objects

# The most direct way of creating a parsetree is to parse the desired text using the spacy language model, then use `ParseTreeDoc.from_spacy()` to construct the `ParseTreeDoc`. The `ParseTreeDoc` object is a container for parsetree objects representing each of the sentences identified with the SpaCy parser.

# In[3]:


spacydoc = nlp(text)
doc = doctable.ParseTreeDoc.from_spacy(spacydoc)
print(f'{len(doc)} sentences of type {type(doc)}')


# The most important arguments to `parse_tok_func` are `text_parse_func` and `userdata_map`.
# 
# 1. `text_parse_func` determines the mapping from a spacy doc object to the text representation of each token accessed through `token.text`. By default this parameter is set to `lambda d: d.text`.
# 
# 2. `userdata_map` is a dictionary mapping an attribute name to a function. You can, for instance, extract info from the original spacy doc object through this method. I'll explain later how these attributes can be accessed and used.

# In[4]:


doc = doctable.ParseTreeDoc.from_spacy(spacydoc, 
    text_parse_func=lambda spacydoc: spacydoc.text,
    userdata_map = {
        'lower': lambda spacydoc: spacydoc.text.lower().strip(),
        'lemma': lambda spacydoc: spacydoc.lemma_,
        'like_num': lambda spacydoc: spacydoc.like_num,
    }
)
print(doc[0]) # show the first sentence


# ## Working With `ParseTree`s
# 
# `ParseTreeDoc` objects represent sequences of `ParseTree` objects identified by the spacy language parser. You can see we can access individual sentence parsetrees using numerical indexing or through iteration.

# In[5]:


print(doc[0])
for sent in doc:
    print(sent)


# Now we will show how to work with `ParseTree` objects. These objects are collections of tokens that can be accessed either as a tree (based on the structure of the dependency tree produced by spacy), or as an ordered sequence. We can use numerical indexing or iteration to interact with individual tokens.

# In[6]:


for token in doc[0]:
    print(token)


# We can work with the tree structure of a `ParseTree` object using the `root` property.

# In[7]:


print(doc[0].root)


# And access the children of a given token using the `childs` property. The following tokens are children of the root token.

# In[8]:


for child in doc[0].root.childs:
    print(child)


# These objects can be serialized using the `.as_dict()` method and de-serialized using the `.from_dict()` method.

# In[9]:


serialized = doc.as_dict()
deserialized = doctable.ParseTreeDoc.from_dict(serialized)
for sent in deserialized:
    print(sent)


# ## More About `Token`s
# Each token in a `ParseTree` is represented by a `Token` object. These objects maintain the tree structure of a parsetree, and each node contains some default information as well as optional and custom information. These are the most important member variables:
# 
# #### Member Variables
# + _i_: index of token in sentence
# + _text_: text representation of token
# + _tag_: the part-of-speech tag offered by the dependency parser (different from POS tagger)
# + _dep_: the dependency relation to parent object. See the [Spacy annotation docs](https://spacy.io/api/annotation#dependency-parsing) for more detail.
# + _parent_: reference to parent node
# + _childs_: list of references to child nodes
# 
# #### Optional Member Variables
# The following are provided if the associated spacy parser component was enabled.
# 
# + _pos_: part-of-speech tag created if user enablled POS 'tagger' in Spacy. See [Spacy POS tag docs](https://spacy.io/api/annotation#pos-tagging) for more detail. Also check out docs for [UPOS tags](https://universaldependencies.org/docs/u/pos/).
# + _ent_: named entity type of token (if NER was enabled when creating parsetree). See [Spacy NER docs](https://spacy.io/api/annotation#named-entities) for more detail.

# In[10]:


for tok in doc[0][:3]:
    print(f"{tok.text}:\n\ti={tok.i}\n\ttag={tok.tag}\n\tdep={tok.dep}\n\tent={tok.ent}\n\tpos={tok.pos}")


# We can also access the custom token properties provided to the `ParseTreeDoc.from_spacy()` method earlier.

# In[11]:


for token in doc[0]:
    print(f"{token.text}: {token['lemma']}")


# ## Recursive Functions on Parsetrees
# 
# We can also navigate the tree structure of parsetrees using recursive functions. Here I simply print out the trajectory of this recursive function.

# In[12]:


def print_recursion(tok, level=0):
    if not tok.childs:
        print('    '*level + 'base node', tok)
    else:
        print('    '*level + 'entering', tok)
        for child in tok.childs:
            print_recursion(child, level+1)
        print('    '*level + 'leaving', tok)

print_recursion(doc[0].root)


# ## Create Using `ParsePipeline`s
# The most common use case, however, probably involves the creation of of a `ParsePipeline` in which the end result will be a `ParseTreeDoc`. We make this using the `get_parsetrees` pipeline component, and here we show several of the possible arguments.
# 

# In[13]:


parser = doctable.ParsePipeline([
    nlp, # the spacy parser
    doctable.Comp('get_parsetrees', **{
        'text_parse_func': lambda spacydoc: spacydoc.text,
        'userdata_map': {
            'lower': lambda spacydoc: spacydoc.text.lower().strip(),
            'lemma': lambda spacydoc: spacydoc.lemma_,
            'like_num': lambda spacydoc: spacydoc.like_num,
        }
    })
])
parser.components


# You can see that the parser provides the same output as we got before with `ParseTreeDoc.from_spacy()`.

# In[14]:


for sent in parser.parse(text):
    print(sent)

