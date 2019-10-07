
# DocTable (slightly more) Advanced Example
In this notebook, I show how to define a DocTable with blob data types, add new rows, and then iterate through rows to populate previously empty fields.


```python
import email
from dt1_helper import get_sklearn_newsgroups # for this example

import sys
sys.path.append('..')
import doctable as dt # this will be the table object we use to interact with our database.
```

## Get News Data From sklearn.datasets
Then parses into a dataframe.


```python
ddf = get_sklearn_newsgroups()
print(ddf.shape)
ddf.head(3)
```

    (11314, 3)





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
      <th>filename</th>
      <th>target</th>
      <th>text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>21379</td>
      <td>soc.religion.christian</td>
      <td>From: kbanner@philae.sas.upenn.edu (Ken Banner...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>20874</td>
      <td>soc.religion.christian</td>
      <td>From: simon@monu6.cc.monash.edu.au\nSubject: S...</td>
    </tr>
    <tr>
      <td>2</td>
      <td>58936</td>
      <td>sci.med</td>
      <td>From: jeffp@vetmed.wsu.edu (Jeff Parke)\nSubje...</td>
    </tr>
  </tbody>
</table>
</div>



## Define NewsGroups DocTable
This definition includes fields file_id, category, raw_text, subject, author, and tokenized_text. The extra columns compared to example_simple.ipynb are for storing extracted metadata.


```python
class NewsGroups(dt.DocTable):
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
```


```python
sng = NewsGroups('news_groupssss.db')
print(sng)
```

    <Documents ct: 0>



```python
# add in raw data
col_order = ('file_id','category','raw_text')
data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
sng.addmany(data,keys=col_order, ifnotunique='ignore')
sng.getdf(limit=2)
```




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
      <th>file_id</th>
      <th>category</th>
      <th>raw_text</th>
      <th>subject</th>
      <th>author</th>
      <th>tokenized_text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>21379</td>
      <td>soc.religion.christian</td>
      <td>From: kbanner@philae.sas.upenn.edu (Ken Banner...</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>20874</td>
      <td>soc.religion.christian</td>
      <td>From: simon@monu6.cc.monash.edu.au\nSubject: S...</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
  </tbody>
</table>
</div>



## Update "tokenized_text" Column
Use .get() to loop through rows in the database, and .update() to add in the newly extracted data. In this case, we simply tokenize the text using the python builtin split() function.


```python
query = sng.get(sel=('file_id','raw_text',))
for row in query:
    
    dat = {'tokenized_text':row['raw_text'].split(),}
    sng.update(dat, 'file_id == {}'.format(row['file_id']))
sng.getdf(limit=2)
```




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
      <th>file_id</th>
      <th>category</th>
      <th>raw_text</th>
      <th>subject</th>
      <th>author</th>
      <th>tokenized_text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>21379</td>
      <td>soc.religion.christian</td>
      <td>From: kbanner@philae.sas.upenn.edu (Ken Banner...</td>
      <td>None</td>
      <td>None</td>
      <td>[From:, kbanner@philae.sas.upenn.edu, (Ken, Ba...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>20874</td>
      <td>soc.religion.christian</td>
      <td>From: simon@monu6.cc.monash.edu.au\nSubject: S...</td>
      <td>None</td>
      <td>None</td>
      <td>[From:, simon@monu6.cc.monash.edu.au, Subject:...</td>
    </tr>
  </tbody>
</table>
</div>



## Extract Email Metadata
This example takes it even further by using the "email" package to parse apart the blog files. It then uses the extracted information to populate the corresponding fields in the DocTable.


```python
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
```




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
      <th>file_id</th>
      <th>category</th>
      <th>raw_text</th>
      <th>subject</th>
      <th>author</th>
      <th>tokenized_text</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>21379</td>
      <td>soc.religion.christian</td>
      <td>From: kbanner@philae.sas.upenn.edu (Ken Banner...</td>
      <td>Re: SATANIC TOUNGES</td>
      <td>kbanner@philae.sas.upenn.edu (Ken Banner)</td>
      <td>[In, article, &lt;May.5.02.53.10.1993.28880@athos...</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>20874</td>
      <td>soc.religion.christian</td>
      <td>From: simon@monu6.cc.monash.edu.au\nSubject: S...</td>
      <td>Saint Story St. Aloysius Gonzaga</td>
      <td>simon@monu6.cc.monash.edu.au</td>
      <td>[Heres, a, story, of, a, Saint, that, people, ...</td>
    </tr>
  </tbody>
</table>
</div>




```python
sng.getdf().to_csv('newsgroup20.csv')
```
