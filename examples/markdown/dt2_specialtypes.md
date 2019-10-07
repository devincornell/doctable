

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
    ('title','string', dict(nullable=False, unique=True)),
    ('bag_of_words','tokens'),
    ('tokenized_sentences', 'subdocs'),
)
db = dt.DocTable2(schema)
print(db)
```

    <DocTable2::_documents_ ct: 0>



```python
tokens = ['this', 'is', 'the', 'happiest', 'day', 'of', 'my', 'life', '.']
db.insert({'title':'Happy sentence', 'bag_of_words':tokens})
db.select(['title','bag_of_words'])
```




    [('Happy sentence', ['this', 'is', 'the', 'happiest', 'day', 'of', 'my', 'life', '.'])]



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
    
    Happy sentences
    [['i', 'am', 'happy', '.'],
     ['the', 'sky', 'is', 'blue', '.'],
     ['sun', 'is', 'shining', '.'],
     ['what', 'more', 'can', 'i', 'ask', 'for', '?']]
    



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
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>0</td>
      <td>1</td>
      <td>Happy sentence</td>
      <td>[this, is, the, happiest, day, of, my, life, .]</td>
      <td>None</td>
    </tr>
    <tr>
      <td>1</td>
      <td>2</td>
      <td>Happy sentences</td>
      <td>None</td>
      <td>[[i, am, happy, .], [the, sky, is, blue, .], [...</td>
    </tr>
  </tbody>
</table>
</div>


