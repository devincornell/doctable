#!/usr/bin/env python
# coding: utf-8

# In[1]:


import sys
sys.path.append('..')
import doctable as dt
import spacy
from pprint import pprint
nlp = spacy.load('en_core_web_sm')#, disable=['ner'])


# In[2]:


exstr = 'Hat is red. He is tall for a dude.'
doc = nlp(exstr)
doc


# ## Making Parsetrees
# 
# By default, `parse_tok_func=None` means it will use the vanilla `dt.DocParser.parse_tok()` method. Often times you may want to pass a lambda function specifying some of the parameters of that function, since it has a number of useful features.
# 
# You can also add additional token properties to the parsetree nodes by setting dictionary values attrname->func in the `info_func_map` parameter.

# In[3]:


parsetrees = dt.DocParser.get_parsetrees(doc, merge_ents=True)
parsetrees


# In[4]:


for pt in parsetrees:
    pt.print_ascii_tree()
    print()


# In[5]:


print([node for node in parsetrees[0]])
print([node.i for node in parsetrees[0]]) # these five properties are inherent
print([node.tok for node in parsetrees[0]])
print([node.dep for node in parsetrees[0]])
print([node.tag for node in parsetrees[0]])
print([node.pos for node in parsetrees[0]])
print([node.info for node in parsetrees[0]]) # info is empty here


# In[6]:


# can also apply information to be added to the .info property of nodes
fm = {'ent': lambda tok: tok.ent_type_}
parsetrees = dt.DocParser.get_parsetrees(doc, merge_ents=True, info_func_map=fm)
print([(node.tok,node.info) for node in parsetrees[1]])


# ### Storing ParseTrees
# For various reasons, you may want to work with parsetrees without the ParseTree object. To do that, you can use the `.asdict()` and `.from_dict()` methods.

# In[7]:


d = parsetrees[0].asdict()
pprint(d)


# In[8]:


d = dt.ParseTree(d).asdict()
pprint(d)


# Because we want to make the pos tags and ner optional, we throw an error when they are accessed but weren't originally included in the parsing.

# In[9]:


nlp2 = spacy.load('en', disable=['ner', 'tagger'])
doc2 = nlp2(exstr)
parsetrees = dt.DocParser.get_parsetrees(doc2, merge_ents=True, info_func_map=fm)
try:
    parsetrees[0][0].ent
except AttributeError:
    print('couldn\'t access .ent')
try:
    parsetrees[0][0].pos
except AttributeError:
    print('couldn\'t access .pos')


# ## Working With ParseTree Objects: Iterative and Recursive
# There are two pimary ways to manipulate ParseTree objects: iteratively and recursively. They can be used iteratively using indexing, slicing, and iterating as one would do with a regular list. The ParseTree object iterates through a list of ParseNode objects which have access to a number of built-in node attributes like .tag, .dep, .tok, and .ent and .pos if NER or tagging were used to parse the spacy doc object.
# 
# Alternatively, one can work with parsetrees recursively. This may be useful if your methods require you to follow chains of tokens. There are two useful built-in methods for working recursively with ParseTree objects: `.bubble_reduce()`, and `.bubble_accum()`.
# 
# **`.bubble_accum()`**: allows you to provide a function that takes a ParseNode and returns a list of objects that will be accumulated after going through the entire parsetree.
# 
# **`.bubble_reduce()`**: allows you to provide a function that takes a ParseNode and an input object and returns an output object. A simple token-counting example is provided below.
# 
# While these methods are useful, you will probably work with ParseNodes directly when writing recursive functions. To do that, access the root-level ParseNode using the `.root` property of the ParseTree object.

# In[10]:


sent = 'Barak Obama is the coolest cat out there.'
doc = nlp(sent)
parsetree = dt.DocParser.get_parsetrees(doc, merge_ents=True, merge_noun_chunks=True)[0]
parsetree, parsetree[0]


# First let's try to get a list of named entities we applied earlier through the `info_func_map` argument of `get_parsetrees()`, both iteratively and recursively.

# In[11]:


# list of ents iteratively
[node for node in parsetree if node.ent]


# In[12]:


# get a list of entities recursively
def get_ents(pnode):
    if pnode.ent != '':
        return [pnode]
    else:
        return []
parsetree.bubble_accum(get_ents)


# In that case, the iterative appears to be easier.
# 
# Now we'll try to identify subject-verb-object triplets both iteratively and recursively.

# In[13]:


# convenience function to help
def child_dep(node, dep_type): # gets first child where node.dep==dep_type.
    for c in node.childs:
        if c.dep == dep_type:
            return c
    return None

def get_triplets(parsetree):
    triplets = list()
    for node in parsetree:
        if node.pos in ['AUX']:
            rel = (child_dep(node,'nsubj'), node, child_dep(node,'attr'))
            triplets.append(rel)
        elif node.pos in ['VERB']:
            rel = (child_dep(node,'nsubj'), node, child_dep(node,'dobj'))
    return triplets
get_triplets(parsetree)


# In[14]:


# convenience function to help
def child_dep(node, dep_type): # gets first child where node.dep==dep_type.
    for c in node.childs:
        if c.dep == dep_type:
            return c
    return None

def get_triplets(pnode):
    if pnode.pos in ['AUX']:
        return [(child_dep(pnode,'nsubj'), pnode, child_dep(pnode,'attr'))]
    elif pnode.pos in ['VERB']:
        return [(child_dep(pnode,'nsubj'), pnode, child_dep(pnode,'dobj'))]
    else:
        return []
parsetree.bubble_accum(get_triplets)


# These two approaches yielded the exact same result with similar code requirements. Here are a few examples of `.bubble_agg()`, a method used to aggregate parsetree info.

# ### Aggregate Method

# In[15]:


# simply count number of nodes
def f(pn,ct):
    return ct + 1
parsetree.bubble_reduce(f, 0)


# In[16]:


# simply accumulate a list of all tokens (same functionality as .accum)
def f(pn,l):
    return l + [pn.tok]
parsetree.bubble_reduce(f, [])


# ### Custom Recursion Function
# To work directly on the parsetree object, use the `.root` property.

# In[17]:


def printnodes(pnode):
    print(pnode.tok, pnode.dep, pnode.pos)
    for child in pnode:
        printnodes(child)

printnodes(parsetree.root)

