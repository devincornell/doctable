```python
import random
import pandas as pd
import numpy as np
from pprint import pprint
import sys
sys.path.append('..')
import doctable as dt
```

## ```tokens``` and ```subdocs``` Custom Types

```tokens``` is used to store a sequence of tokens and ```subdocs``` is used to store a sequence of a sequence of tokens (think list of tokenized sentences). Simply specify these columns as their appropriate type and it will automatically convert these tokenized objects to formatted strings for database storage.


```python
schema = (
    ('id','integer',dict(primary_key=True, autoincrement=True)),
    ('title','string', dict(nullable=False)),
    ('bag_of_words','tokens'),
    ('tokenized_sentences', 'tokens'),
    ('paragraphs', 'tokens'),
    ('data', 'cpickle'),
)
db = dt.DocTable2(schema)
print(db)
```

    <DocTable2::_documents_ ct: 0>



```python
tokens = ['this', 'is', 'the', 'happiest', 'day', 'of', 'my', 'life', '.']
db.insert({'title':'Happy sentence', 'bag_of_words':tokens})
db.insert({'title':'Happy nothing'})
db.select(['title','bag_of_words'])
```




    [('Happy sentence', ('this', 'is', 'the', 'happiest', 'day', 'of', 'my', 'life', '.')),
     ('Happy nothing', None)]



Under the hood, DocTable2 stores a ```tokens``` column as a set of strings separated by newlines. This is more efficient than storing a pickled list or other sequence because large files can compress text data efficiently.


```python
sentences = (
    ('i', 'am', 'happy','.'),
    ('the','sky','is','blue','.'),
    ('sun', 'is', 'shining','.'),
    ('what', 'more', 'can', 'i', 'ask', 'for', '?'),
)

db.insert({'title':'Happy sentences', 'tokenized_sentences':sentences})
for title,sents in db.select(['title','tokenized_sentences']):
    print(title)
    pprint(sents)
    print()
```

    Happy sentence
    None
    
    Happy nothing
    None
    
    Happy sentences
    (('i', 'am', 'happy', '.'),
     ('the', 'sky', 'is', 'blue', '.'),
     ('sun', 'is', 'shining', '.'),
     ('what', 'more', 'can', 'i', 'ask', 'for', '?'))
    



```python
paragraphs = (
    (
        ('i', 'am', 'happy','.'),
        ('the','sky','is','blue','.'),
    ),
    (
        ('sun', 'is', 'shining','.'),
        ('what', 'more', 'can', 'i', 'ask', 'for', '?'),
    )
)

db.insert({'title':'Happy paragraphs', 'paragraphs':paragraphs}, ifnotunique='replace')
for title,paragraphs in db.select(['title','paragraphs']):
    print(title)
    pprint(paragraphs)
    print()
```

    Happy sentence
    None
    
    Happy nothing
    None
    
    Happy sentences
    None
    
    Happy paragraphs
    ((('i', 'am', 'happy', '.'), ('the', 'sky', 'is', 'blue', '.')),
     (('sun', 'is', 'shining', '.'),
      ('what', 'more', 'can', 'i', 'ask', 'for', '?')))
    



```python
data = {'hello':0, 'world':1}
db.insert({'title':'my data', 'data':data}, ifnotunique='replace')
for title,data in db.select(['title','data']):
    print(title)
    pprint(data)
    print()
```

    Happy sentence
    None
    
    Happy nothing
    None
    
    Happy sentences
    None
    
    Happy paragraphs
    None
    
    my data
    {'hello': 0, 'world': 1}
    



```python
db.select_df()
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
      <th>title</th>
      <th>bag_of_words</th>
      <th>tokenized_sentences</th>
      <th>paragraphs</th>
      <th>data</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>Happy sentence</td>
      <td>(this, is, the, happiest, day, of, my, life, .)</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>Happy nothing</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <td>2</td>
      <td>3</td>
      <td>Happy sentences</td>
      <td>None</td>
      <td>((i, am, happy, .), (the, sky, is, blue, .), (...</td>
      <td>None</td>
      <td>None</td>
    </tr>
    <tr>
      <td>3</td>
      <td>4</td>
      <td>Happy paragraphs</td>
      <td>None</td>
      <td>None</td>
      <td>(((i, am, happy, .), (the, sky, is, blue, .)),...</td>
      <td>None</td>
    </tr>
    <tr>
      <td>4</td>
      <td>5</td>
      <td>my data</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>{'hello': 0, 'world': 1}</td>
    </tr>
  </tbody>
</table>
</div>


