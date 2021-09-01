#!/usr/bin/env python
# coding: utf-8

# # Vignette 3: Storing Parsed Documents
# 
# Here I'll show how to make a DocTable for storing NSS documents at the paragraph level, and parse the documents in parallel.
# 
# For context, check out [Example 1](https://devincornell.github.io/doctable/examples/ex_nss.html) - here we'll just use some shortcuts for code used there. These come from the util.py code in the repo examples folder.
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
#import util
import doctable
import spacy
from tqdm import tqdm

# automatically clean up temp folder after python ends
tmpfolder = doctable.TempFolder('tmp')


# First we define the metadata and download the text data.

# In[2]:


import urllib
def download_nss(year):
    ''' Simple helper function for downloading texts from my nssdocs repo.'''
    baseurl = 'https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/{}.txt'
    url = baseurl.format(year)
    text = urllib.request.urlopen(url).read().decode('utf-8')
    return text

document_metadata = [
    {'year': 2000, 'party': 'D', 'president': 'Clinton'},
    {'year': 2006, 'party': 'R', 'president': 'W. Bush'}, 
    {'year': 2015, 'party': 'D', 'president': 'Obama'}, 
    {'year': 2017, 'party': 'R', 'president': 'Trump'}, 
]

sep = '\n\n'
first_n = 10
for md in document_metadata:
    text = download_nss(md['year'])
    md['text'] = sep.join(text.split(sep)[:first_n])
print(f"{len(document_metadata[0]['text'])=}")


# ## 1. Define the DocTable Schema
# Now we define a doctable schema using the `doctable.schema` class decorator and the [pickle file column type](examples/doctable_file_column_types.html) to prepare to store parsetrees as binary data.

# In[3]:


# to be used as a database row representing a single NSS document
@doctable.schema
class NSSDoc:
    __slots__ = [] # include so that doctable.schema can create a slot class
    
    id: int = doctable.IDCol() # this is an alias for doctable.Col(primary_key=True, autoincrement=True)
    year: int =  doctable.Col()
    party: str = doctable.Col()
    president: str = doctable.Col()
    text: str = doctable.Col()
    doc: doctable.ParseTreeDoc = doctable.ParseTreeFileCol('tmp/parsetree_pickle_files')


# In[4]:


doctable.ParseTreeFileCol('tmp/parsetree_pickle_files')


# And a class to represent an NSS DocTable.

# In[5]:


class NSSDocTable(doctable.DocTable):
    _tabname_ = 'nss_documents'
    _schema_ = NSSDoc
    
nss_table = NSSDocTable(target='tmp/nss_3.db', new_db=True)
nss_table.count()


# In[ ]:


for md in document_metadata:
    nss_table.insert(md)
nss_table.head()


# ## 2. Create a Parser Class Using a Pipeline
# Now we create a small `NSSParser` class that keeps a `doctable.ParsePipeline` object for doing the actual text processing. As you can see from our init method, instantiating the package will load a spacy module into memory and construct the pipeline from the selected components. We also create a wrapper over the pipeline `.parse` and `.parsemany` methods. Here we define, instantiate, and view the components of `NSSParser`.

# In[ ]:


class NSSParser:
    ''' Handles text parsing for NSS documents.'''
    def __init__(self):
        nlp = spacy.load('en_core_web_sm')
        
        # this determines all settings for tokenizing
        self.pipeline = doctable.ParsePipeline([
            nlp, # first run spacy parser
            doctable.Comp('merge_tok_spans', merge_ents=True),
            doctable.Comp('get_parsetrees', **{
                'text_parse_func': doctable.Comp('parse_tok', **{
                    'format_ents': True,
                    'num_replacement': 'NUM',
                })
            })
        ])
    
    def parse(self, text):
        return self.pipeline.parse(text)

parser = NSSParser() # creates a parser instance
parser.pipeline.components


# Now we parse the paragraphs of each document in parallel.

# In[ ]:


for doc in tqdm(nss_table.select(['id','year','text'])):
    parsed = parser.parse(doc.text)
    nss_table.update({'doc': parsed}, where=nss_table['id']==doc.id)
nss_table.select_df(limit=2)


# ## 3. Work With Parsetrees
# 
# Now that we have stored our parsed text as files in the database, we can manipulate the parsetrees. This example shows the 5 most common nouns from each national security strategy document. This is possible because the `doctable.ParseTree` data structures contain `pos` information originally provided by the spacy parser. Using `ParseTreeFileType` allows us to more efficiently store pickled binary data so that we can perform these kinds of analyses at scale.

# In[ ]:


from collections import Counter # used to count tokens

for nss in nss_table.select():
    noun_counts = Counter([tok.text for pt in nss.doc for tok in pt if tok.pos == 'NOUN'])
    print(f"{nss.president} ({nss.year}): {noun_counts.most_common(5)}")


# Definitely check out this [example on parsetreedocs](examples/doctable_parsetreedoc_column.html) if you're interested in more applications.
# 
# And that is all for this vignette! See the list of vignettes at the top of this page for more examples.
