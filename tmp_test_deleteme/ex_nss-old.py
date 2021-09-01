#!/usr/bin/env python
# coding: utf-8

# # doctable Demo: US National Security Strategy Documents
# This example shows a full example of a doctable workflow designed to parse texts end-to-end, using the NSS documents for demonstation.

# In[1]:


import sys
sys.path.append('..')
import doctable as dt
import spacy
import os
from pprint import pprint
import urllib.request # used for downloading nss docs


# ## Intro to Dataset
# This dataset is the plain text version of the US National Security Strategy documents. During the parsing process, all plain text files will be downloaded from my [github project hosting the nss docs](https://github.com/devincornell/nssdocs). I compiled the metadata you see below from [a page hosted by the historical dept of the secretary's office](https://history.defense.gov/Historical-Sources/National-Security-Strategy/). In short, each US President must release at least one NSS per term, with some (namely Clinton) producing more than one per term.
# 
# In this example, I'll show how to create a database for document + metadata storage using the `DocTable` class, and a parser class using `DocParser`. We will store the metadata you see below in addition to the formatted document text.

# In[2]:


nss_metadata = {1993: {'party': 'R', 'president': 'H.W. Bush'}, 
            2002: {'party': 'R', 'president': 'W. Bush'}, 
            2015: {'party': 'D', 'president': 'Obama'}, 
            1994: {'party': 'D', 'president': 'Clinton'}, 
            1990: {'party': 'R', 'president': 'H.W. Bush'}, 
            1991: {'party': 'R', 'president': 'H.W. Bush'}, 
            2006: {'party': 'R', 'president': 'W. Bush'}, 
            1997: {'party': 'D', 'president': 'Clinton'}, 
            1995: {'party': 'D', 'president': 'Clinton'}, 
            1987: {'party': 'R', 'president': 'Reagan'}, 
            1988: {'party': 'R', 'president': 'Reagan'}, 
            2017: {'party': 'R', 'president': 'Trump'}, 
            1996: {'party': 'D', 'president': 'Clinton'}, 
            2010: {'party': 'D', 'president': 'Obama'}, 
            1999: {'party': 'D', 'president': 'Clinton'}, 
            1998: {'party': 'D', 'president': 'Clinton'}, 
            2000: {'party': 'D', 'president': 'Clinton'}
}


# ## Create a DocTable-based Class
# This class inherits from DocTable and will typically store schema and other static inforamtion about the database. This is the most common way to work with DocTable. You can see we keep two class member variables to store the database table name and the schema. See the [schema guide](examples/doctable_schema.html) for more schema examples.
# 
# We also create a `.insert_nssdoc()` method which wraps the `DocTable.insert()` method to make insertion easier by counting paragraphs, sentences, and tokens to insert. A `.print_doctable()` static method is created so we can print the contents of a NSSDocs database later.

# In[3]:


class NSSDocs(dt.DocTable):
    tabname = 'nssdocs'
    schema = (
        ('integer', 'id', dict(primary_key=True, autoincrement=True)),
        ('integer', 'year', dict(unique=True, nullable=False)),
        ('string','president'),
        ('string','party'), ('check_constraint', 'party in ("R","D")'),
        ('integer','num_pars'),
        ('integer','num_sents'),
        ('integer', 'num_toks'),
        ('pickle','par_sents'), # nested tokens within sentences within paragraphs
        ('index', 'ind_yr', ['year'], dict(unique=True)),        
    )
    def __init__(self, **kwargs):
        dt.DocTable.__init__(self, schema=self.schema, tabname=self.tabname, **kwargs)
        
    def insert_nssdoc(self, year, par_sents, prez, party, **kwargs):
        self.insert({
            'year': year,
            'president': prez,
            'party': party,
            'num_pars': len(par_sents),
            'num_sents': len([s for par in par_sents for s in par]),
            'num_toks': len([t for par in par_sents for s in par for t in s]),
            'par_sents': par_sents,
        }, **kwargs)
    
    @staticmethod
    def print_doctable(fname):
        '''Simple method for printing contents of a doctable.'''
        db = NSSDocs(fname=fname)
        print(db)
        print(db.select_df(limit=2))


# We can then create a connection to a database by instantiating. Since the fname parameter was not provided, this doctable exists only in memory using sqlite. Our other examples will use files, but instantiating in memory first is a good way to check that the schema is valid. We can check the sqlite table schema using the `.schemainfo` property. You can see that the 'pickle' datatype we chose above is represented as a BLOB column. This is because DocTable, using SQLAlchemy core, creates an interface on top of sqlite to handle the data conversion.

# In[4]:


db = NSSDocs()
db.schemainfo


# ## Create a Parser Class
# Now we create a parser class NSSParser which inherits from DocParser. This class will handle parsing the text data and inserting it into the DocTable. This is the most common way to use the DocParser class; it allows our NSSParser to have access to the flexible functions. You can see more of these methods in the [DocParser reference](ref/doctable.DocParser.html) or the [overview examples](examples/docparser_basics.html).
# 
# The `parse_nss_docs()` method we created here shows the use of the `DocParser.distribute_chunks()` method which can take an input sequence, in our case a list of years as integers, and break it up into chunks to send to a user-provided function, in this case our `.parse_nss_chunk()`. This function handles a batch of years and for each year will download the texts (from my [nssdocs github repo](https://github.com/devincornell/nssdocs)), split them into paragraphs, parse them using spacy, and tokenize or convert to parsetrees using the `DocParser.tokenize_doc()` and `DocParser.get_parsetree()` methods respectively. Note that we can see the `DocParser.preprocess()` method used for preprocessing and the `DocParser.use_tok()` and `DocParser.parse_tok()` methods, wrapped in lambda functions, passed to `DocParser.tokenize_doc()` method for extra control over the parsing.

# In[5]:


class NSSParser(dt.DocParser):
    ''''''
    years_default = (1987, 1988, 1990, 1991, 1993, 1994, 1995, 
                     1996, 1997, 1998, 1999, 2000, 2002, 2006, 
                     2010, 2015, 2017)
    
    def __init__(self, dbfname, metadata, *args, **kwargs):
        self.nlp = spacy.load('en')
        self.dbfname = dbfname
        self.metadata = metadata
        
    def parse_nss_docs(self, years=None, as_parsetree=False, workers=None, verbose=False):
        '''Parse and store nss docs into a doctable.
        Args:
            years (list): years to request from the nss corpus
            dbfname (str): fname for DocTable to initialize in each process.
            as_parsetree (bool): store parsetrees (True) or tokens (False)
            workers (int or None): number of processes to create for parsing.
        '''
        if years is None:
            years = self.years_default
        self.distribute_chunks(self.parse_nss_chunk, years, self.nlp, self.dbfname, 
                               as_parsetree, verbose, self.metadata, workers=workers)
    
    @classmethod
    def parse_nss_chunk(cls, years, nlp, dbfname, as_parsetree, verbose, metadata):
        '''Runs in separate process for each chunk of nss docs.
        Description: each 
        Args:
            years (list<int>): years of nss to download and parse
            nlp (spacy parser object): process documents using nlp.pipe()
            dbfname (str): filename of NSSDocs database to open
            as_parsetree (bool): parse into parsetree or just tokens.
                storing parsetrees is much more (~6x) expensive than
                just storing tokens.
        '''
        
        # create a new database connection
        db = NSSDocs(fname=dbfname)
        
        # download, preprocess, and break texts into paragraphs
        preprocess = lambda text: cls.preprocess(text, replace_xml='')
        texts = list(map(preprocess, list(map(cls.download_nss, years))))
        pars = [(i,par.strip()) for i,text in enumerate(texts) 
                      for par in text.split('\n\n') if len(par.strip()) > 0]
        ind, pars = list(zip(*pars))
        
        use_tok = lambda tok: cls.use_tok(tok, filter_whitespace=True)
        parse_tok = lambda tok: cls.parse_tok(tok, replace_num=True, format_ents=True)
        
        # choose to create either token sequences or parsetrees
        if not as_parsetree:
            tokenize = lambda doc: cls.tokenize_doc(doc, merge_ents=True, split_sents=True, parse_tok_func=parse_tok, use_tok_func=use_tok)
        else:
            tokenize = lambda doc: cls.get_parsetrees(doc, merge_ents=True, parse_tok_func=parse_tok)
        
        if verbose: print('starting', years)
        # process documents
        pp = list()
        for doc in nlp.pipe(pars):
            toks = tokenize(doc)
            pp.append(toks)
        if verbose: print('about to insert', years)
        # merge paragraphs back into docs and insert into db
        doc_pars = [[p for idx,p in zip(ind,pp) if idx==i] for i in range(max(ind)+1)]
        for yr,dp in zip(years,doc_pars):
            prez = metadata[yr]['president']
            party = metadata[yr]['party']
            db.insert_nssdoc(yr, dp, prez, party, ifnotunique='replace')
        if verbose: print('inserted', years)

            
    @staticmethod
    def download_nss(year):
        '''Simple helper function for downloading texts from my nssdocs repo.'''
        baseurl = 'https://raw.githubusercontent.com/devincornell/nssdocs/master/docs/{}.txt'
        url = baseurl.format(year)
        text = urllib.request.urlopen(url).read().decode('utf-8')
        return text


# ## Run the Parser
# Now we run the parsing algorithm by instantiating NSSParser (which simply loads a spacy module) and parse the documents using the method we created `.parse_nss_docs()`. From looking at the `.parse_nss_chunk()` method above, you can see that each process is passed only a year and a doctable filename, and each process will download a copy of the given document, process the document, and insert the document into its own DocTable connection.
# 
# In this first example you can see the print output from each of the processes as they act simultaneously and then insert their results into their doctable.

# In[6]:


# instantiate parser (loads spacy model) and call .parse_nss_docs() to parse and store the docs
fname_tokens = 'exdb/ex_workflow_tokens.db'
parser = NSSParser(fname_tokens, nss_metadata)
get_ipython().run_line_magic('time', 'parser.parse_nss_docs(as_parsetree=False, workers=4, verbose=True)')
NSSDocs.print_doctable(fname_tokens)


# In[16]:


# by omitting the "workers" parameter, DocParser will use all the cores the machine has
get_ipython().run_line_magic('time', 'parser.parse_nss_docs(as_parsetree=False)')
NSSDocs.print_doctable(fname_tokens)


# In[17]:


# now we set "as_parsetree" to true so it will store the docs as parstrees instead of tokens.
fname_parsetrees = 'exdb/ex_workflow_parsetrees.db'
parser = NSSParser(fname_parsetrees, nss_metadata)
get_ipython().run_line_magic('time', 'parser.parse_nss_docs(as_parsetree=True)')
NSSDocs.print_doctable(fname_parsetrees)


# ### Filesize Comparison
# While the timed performance of generating parsetrees vs tokens is relatively insignificant, we see a huge difference in the resulting database file sizes. Wheras the tokens database took about 6 MB, the parsetree database took about 40 MB. A significant difference worth consideration in your analyses.

# In[18]:


os.path.getsize(fname_tokens)/1e6, os.path.getsize(fname_parsetrees)/1e6


# ## Read Database
# Now we can use DocTable to view and manipulate the stored documents.

# In[19]:


db = NSSDocs(fname=fname_tokens)
db


# In[20]:


# here we show some metatadat from the new corpus
df = db.select_df(['year','president', 'party', 'num_pars', 'num_sents', 'num_toks'])
print('This corpus consists of {} documents, {} paragraphs, {} sentences, and {} tokens.'
      ''.format(df.shape[0], df['num_pars'].sum(), df['num_sents'].sum(), df['num_toks'].sum()))
df


# In[21]:


def get_sents(db):
    for doc in db.select('par_sents'):
        for par in doc:
            for sent in par:
                yield sent
sents = list(get_sents(db))
sents[0][:5], sents[1][:5]


# ### Conclusions
# This example shows a very common way of working with the doctable package. Wheras the DocTable class provides a simple interface for storing and accessing databases, DocParser provides convenient methods for processing texts in parallel.

# # Training Models in Parallel
# Now we want to train several ml models on the data, one for each parmeter configuration. We can train multiple models in the same way that we parse text by using the `.DocParser.distribute_process()` method, where we provide a function that takes the input data and trains a model and then stores the result in a database. This will allow you to take full advantage of your computing machinery.
# 
# Our example will be in measuring classification accuracy for predicting the document from which a given NSS paragraph was drawn. To do this, we extract all paragraphs from the documents, train a model pipeline including TF-IDF, SVD, and an SVM classifier to predict the nss document given a set of paragraph tokens, and report cross-validation results.
# 
# First we create a new ModelDB class which inherits from DocTable, then we create a `train_model()` function which takes the number of features as a parameter. The function trains a model and saves the number of features used as well as the result metrics to the database. Because we use `DocTable.distribute_process()`, these models are all trained in parallel and saved to the db when finished.

# In[23]:


# extracts a list of paragraph tokens from all docs, records year from which each par came
pars = [(pty,par) for pty,doc in db.select(['party','par_sents']) for par in doc]
party, paragraphs = list(zip(*pars))
paragraphs = [[tok for sent in par for tok in sent if isinstance(tok,str)] for par in paragraphs]


# In[25]:


# create a new database to store the models
class ModelDB(dt.DocTable):
    tabname = 'modeldb'
    schema = (
        ('integer', 'id', dict(primary_key=True, autoincrement=True)),
        ('integer', 'num_feat', dict(unique=True)),
        ('float', 'train_time'),
        ('float', 'av_train'),
        ('float', 'av_test'),
    )
    def __init__(self, **kwargs):
        super().__init__(schema=self.schema, tabname=self.tabname, **kwargs)
fname_models = 'exdb/nss_models.db'
modeldb = ModelDB(fname=fname_models)
modeldb.delete()
modeldb


# In[26]:


# sklearn imports
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import cross_validate
from sklearn.decomposition import PCA, SparsePCA, TruncatedSVD


# In[27]:


def train_model(num_feat, pars, party, fname):
    '''Function to train a single model.'''
    pipeline = Pipeline([
        ('vect', CountVectorizer(tokenizer=lambda x:x, preprocessor=lambda x:x, min_df=10)),
        ('tfidf', TfidfTransformer()),
        ('svd', TruncatedSVD(n_components=num_feat)),
        ('clf', SGDClassifier()),
    ])
    
    scores = cross_validate(pipeline, pars, party, cv=5, return_train_score=True)
    db = ModelDB(fname=fname)
    db.insert({
        'num_feat': num_feat,
        'train_time': scores['fit_time'].mean(),
        'av_train': scores['train_score'].mean(),
        'av_test': scores['test_score'].mean(),
    }, ifnotunique='replace')
    return scores['test_score'].mean()


# In[30]:


num_feat_list = (500, 1000, 1500, 2000)

dt.DocParser.distribute_process(train_model, num_feat_list, paragraphs, party, fname_models)
modeldb.select_df()


# ## Conclusions
# This example shows how we can use DocTable for parsing texts and for training models in parallel. Databases make it easy to parallelize tasks across processes because the results can be stored in a table that is thread-safe.
