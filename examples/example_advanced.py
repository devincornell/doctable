
# coding: utf-8

# # DocTable (slightly more) Advanced Example
# In this notebook, I show how to define a DocTable with blob data types, add new rows, and then iterate through rows to populate previously empty fields.

# In[1]:


import email
from example_helper import get_sklearn_newsgroups # for this example

from doctable import DocTable # this will be the table object we use to interact with our database.


# ## Get News Data From sklearn.datasets
# Then parses into a dataframe.

# In[2]:


ddf = get_sklearn_newsgroups()
print(ddf.shape)
ddf.head(3)


# ## Define NewsGroups DocTable
# This definition includes fields file_id, category, raw_text, subject, author, and tokenized_text. The extra columns compared to example_simple.ipynb are for storing extracted metadata.

# In[3]:


class NewsGroups(DocTable):
    def __init__(self, fname):
        '''
            DocTable class.
            Inputs:
                fname: fname is the name of the new sqlite database that will be used for instances of class.
        '''
        tabname = 'newsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema=(
                'id integer primary key autoincrement',
                'file_id int', 
                'category string',
                'raw_text string',
                'subject string', 
                'author string', 
                'tokenized_text blob', 
            ),
            constraints=('UNIQUE(file_id)',)
        )
        
        # create indices on file_id and category
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")


# In[4]:


sng = NewsGroups('news_groupdd.db')
print(sng)


# In[5]:


# add in raw data
col_order = ('file_id','category','raw_text')
data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
sng.addmany(data,keys=col_order, ifnotunique='ignore')
sng.getdf(limit=2)


# ## Update "tokenized_text" Column
# Use .get() to loop through rows in the database, and .update() to add in the newly extracted data. In this case, we simply tokenize the text using the python builtin split() function.

# In[7]:


query = sng.get(sel=('file_id','raw_text',))
for row in query:
    
    dat = {'tokenized_text':row['raw_text'].split(),}
    sng.update(dat, 'file_id == {}'.format(row['file_id']))
sng.getdf(limit=2)


# ## Extract Email Metadata
# This example takes it even further by using the "email" package to parse apart the blog files. It then uses the extracted information to populate the corresponding fields in the DocTable.

# In[ ]:


query = sng.get(sel=('file_id','raw_text',), asdict=False)
for fid,text in query:
    e = email.message_from_string(text)
    auth = e['From'] if 'From' in e.keys() else ''
    subj = e['Subject'] if 'Subject' in e.keys() else ''
    tok = e.get_payload().split()
    dat = {
        'tokenized_text':tok,
        'author':auth,
        'subject':subj,
    }
    
    sng.update(dat, 'file_id == {}'.format(fid))
sng.getdf(limit=2)


# In[ ]:


sng.getdf().to_csv('newsgroup20.csv')

