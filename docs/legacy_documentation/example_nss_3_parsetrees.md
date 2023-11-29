# Vignette 3: Storing Parsed Documents

Here I'll show how to make a DocTable for storing NSS documents at the paragraph level, and parse the documents in parallel.

For context, check out [Example 1](https://devincornell.github.io/doctable/examples/ex_nss.html) - here we'll just use some shortcuts for code used there. These come from the util.py code in the repo examples folder.

These are the vignettes I have created:

+ [1: Storing Document Metadata](example_nss_1_intro.html)

+ [2: Storing Document Text](example_nss_2_parsing.html)

+ [3: Storing Parsed Documents](example_nss_3_parsetrees.html)


```python
import sys
sys.path.append('..')
#import util
import doctable
import spacy
from tqdm import tqdm

# automatically clean up temp folder after python ends
import tempfile
tempdir = tempfile.TemporaryDirectory()
tmpfolder = tempdir.name
tmpfolder
```




    '/tmp/tmp1isfmada'



First we define the metadata and download the text data.


```python
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
```

    len(document_metadata[0]['text'])=6695


## 1. Define the DocTable Schema
Now we define a doctable schema using the `doctable.schema` class decorator and the [pickle file column type](examples/doctable_file_column_types.html) to prepare to store parsetrees as binary data.


```python
# to be used as a database row representing a single NSS document
@doctable.schema
class NSSDoc:
    __slots__ = [] # include so that doctable.schema can create a slot class
    
    id: int = doctable.IDCol() # this is an alias for doctable.Col(primary_key=True, autoincrement=True)
    year: int =  doctable.Col()
    party: str = doctable.Col()
    president: str = doctable.Col()
    text: str = doctable.Col()
    doc: doctable.ParseTreeDoc = doctable.ParseTreeFileCol(f'{tmpfolder}/parsetree_pickle_files')
```

And a class to represent an NSS DocTable.


```python
class NSSDocTable(doctable.DocTable):
    _tabname_ = 'nss_documents'
    _schema_ = NSSDoc
    
nss_table = NSSDocTable(target=f'{tmpfolder}/nss_3.db', new_db=True)
print(nss_table.count())
nss_table.schema_table()
```

    0


    /DataDrive/code/doctable/examples/../doctable/doctable.py:402: UserWarning: Method .count() is depricated. Please use .q.count() instead.
      warnings.warn('Method .count() is depricated. Please use .q.count() instead.')





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>name</th>
      <th>type</th>
      <th>nullable</th>
      <th>default</th>
      <th>autoincrement</th>
      <th>primary_key</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>id</td>
      <td>INTEGER</td>
      <td>False</td>
      <td>None</td>
      <td>auto</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>year</td>
      <td>INTEGER</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>party</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>president</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>text</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>doc</td>
      <td>VARCHAR</td>
      <td>True</td>
      <td>None</td>
      <td>auto</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
for md in document_metadata:
    nss_table.insert(md)
nss_table.head()
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:364: UserWarning: Method .insert() is depricated. Please use .q.insert_single(), .q.insert_single_raw(), .q.insert_multi(), or .q.insert_multi() instead.
      warnings.warn('Method .insert() is depricated. Please use .q.insert_single(), '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:390: UserWarning: .insert_single() is depricated: please use .q.insert_single() or .q.insert_single_raw()
      warnings.warn(f'.insert_single() is depricated: please use .q.insert_single() or '
    /DataDrive/code/doctable/examples/../doctable/doctable.py:407: UserWarning: Method .head() is depricated. Please use .q.select_head() instead.
      warnings.warn('Method .head() is depricated. Please use .q.select_head() instead.')
    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: TypeDecorator ParseTreeDocFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>id</th>
      <th>year</th>
      <th>party</th>
      <th>president</th>
      <th>text</th>
      <th>doc</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>2000</td>
      <td>D</td>
      <td>Clinton</td>
      <td>As we enter the new millennium, we are blessed...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2006</td>
      <td>R</td>
      <td>W. Bush</td>
      <td>My fellow Americans, \n\nAmerica is at war. Th...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2015</td>
      <td>D</td>
      <td>Obama</td>
      <td>Today, the United States is stronger and bette...</td>
      <td>None</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>2017</td>
      <td>R</td>
      <td>Trump</td>
      <td>An America that is safe, prosperous, and free ...</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



## 2. Create a Parser Class Using a Pipeline
Now we create a small `NSSParser` class that keeps a `doctable.ParsePipeline` object for doing the actual text processing. As you can see from our init method, instantiating the package will load a spacy module into memory and construct the pipeline from the selected components. We also create a wrapper over the pipeline `.parse` and `.parsemany` methods. Here we define, instantiate, and view the components of `NSSParser`.


```python
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
```




    [<spacy.lang.en.English at 0x7fedee1c2cd0>,
     functools.partial(<function merge_tok_spans at 0x7fedf2d8f040>, merge_ents=True),
     functools.partial(<function get_parsetrees at 0x7fedf2d8f1f0>, text_parse_func=functools.partial(<function parse_tok at 0x7fedf2d82ee0>, format_ents=True, num_replacement='NUM'))]



Now we parse the paragraphs of each document in parallel.


```python
for doc in tqdm(nss_table.select(['id','year','text'])):
    parsed = parser.parse(doc.text)
    #print(parsed.as_dict())
    #break
    print(nss_table['doc'])
    nss_table.update({'doc': parsed}, where=nss_table['id']==doc.id, verbose=True)
#nss_table.select_df(limit=2)
```

    /DataDrive/code/doctable/examples/../doctable/doctable.py:443: UserWarning: Method .select() is depricated. Please use .q.select() instead.
      warnings.warn('Method .select() is depricated. Please use .q.select() instead.')
      0%|                                                                                                                                                      | 0/4 [00:00<?, ?it/s]/DataDrive/code/doctable/examples/../doctable/doctable.py:489: UserWarning: Method .update() is depricated. Please use .q.update() instead.
      warnings.warn('Method .update() is depricated. Please use .q.update() instead.')
     25%|███████████████████████████████████▌                                                                                                          | 1/4 [00:00<00:00,  3.83it/s]

    nss_documents.doc
    DocTable: UPDATE nss_documents SET doc=? WHERE nss_documents.id = ?
    nss_documents.doc
    DocTable: UPDATE nss_documents SET doc=? WHERE nss_documents.id = ?


    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 4/4 [00:00<00:00,  4.89it/s]

    nss_documents.doc
    DocTable: UPDATE nss_documents SET doc=? WHERE nss_documents.id = ?
    nss_documents.doc
    DocTable: UPDATE nss_documents SET doc=? WHERE nss_documents.id = ?


    


## 3. Work With Parsetrees

Now that we have stored our parsed text as files in the database, we can manipulate the parsetrees. This example shows the 5 most common nouns from each national security strategy document. This is possible because the `doctable.ParseTree` data structures contain `pos` information originally provided by the spacy parser. Using `ParseTreeFileType` allows us to more efficiently store pickled binary data so that we can perform these kinds of analyses at scale.


```python
from collections import Counter # used to count tokens

for nss in nss_table.select():
    noun_counts = Counter([tok.text for pt in nss.doc for tok in pt if tok.pos == 'NOUN'])
    print(f"{nss.president} ({nss.year}): {noun_counts.most_common(5)}")
```

    Clinton (2000): [('world', 9), ('security', 9), ('prosperity', 7), ('threats', 5), ('efforts', 5)]
    W. Bush (2006): [('people', 4), ('world', 3), ('war', 2), ('security', 2), ('strategy', 2)]
    Obama (2015): [('security', 15), ('world', 9), ('opportunities', 7), ('strength', 7), ('challenges', 7)]
    Trump (2017): [('government', 5), ('principles', 4), ('peace', 3), ('people', 3), ('world', 3)]


    /DataDrive/code/doctable/examples/../doctable/connectengine.py:69: SAWarning: TypeDecorator ParseTreeDocFileType() will not produce a cache key because the ``cache_ok`` attribute is not set to True.  This can have significant performance implications including some performance degradations in comparison to prior SQLAlchemy versions.  Set this attribute to True if this type object's state is safe to use in a cache key, or False to disable this warning. (Background on this error at: https://sqlalche.me/e/14/cprf)
      return self._engine.execute(query, *args, **kwargs)


Definitely check out this [example on parsetreedocs](examples/doctable_parsetreedoc_column.html) if you're interested in more applications.

And that is all for this vignette! See the list of vignettes at the top of this page for more examples.
