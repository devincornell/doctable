# Pickle / JSON / Token (DocTable Datatype) Experiments

Conclusions:
* my custom tokenization algorithm is worse on every measure
* pickle/cpickle is 5x as fast as json at serializing
* pickle/cpickle is 10x as fast as json at deserializing
* pickle/cpickle creates 10x as small compressed data
* numpy .tobytes() is ~30% faster at serialization compared to pickle/cpickle, same serialized size
* numpy .frombytes is 5x faster than pickle/cpickle


```python
import sys
sys.path.append('..')
from doctable.coltypes import store_tokens, load_tokens
import os
import random
import _pickle
import pickle
import json
import numpy as np
class DevinToks:
    @staticmethod
    def dumps(toks):
        return store_tokens(toks)
    @staticmethod
    def loads(tokdat):
        return load_tokens(tokdat)
```


```python
# try tuples
def random_paragraphs(n_par=1000, n_sent=1000, n_tok=20):
    pars = tuple([
        tuple([
            tuple(['abcdslkjkljaghjk' for _ in range(n_tok)])
            for _ in range(n_sent)
        ])
        for _ in range(n_par)
    ])
    return pars
paragraphs = random_paragraphs(10000)
len([t for sent in paragraphs for t in sent])
```




    10000000




```python
# try lists
def random_paragraphs_list(n_par=1000, n_sent=1000, n_tok=20):
    pars = [
        [
            ['abcdslkjkljaghjk' for _ in range(n_tok)]
            for _ in range(n_sent)
        ]
        for _ in range(n_par)
    ]
    return pars
list_pars = random_paragraphs_list(10)
len([t for sent in list_pars for t in sent])
```




    10000




```python
# test serialization
def test_dump(pars, serializer):
    return serializer.dumps(pars)
%timeit test_dump(paragraphs,DevinToks)
%timeit test_dump(paragraphs,pickle)
%timeit test_dump(paragraphs,_pickle)
%timeit test_dump(paragraphs,json)
```

    1min 48s ± 132 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    7.62 s ± 40.4 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    7.65 s ± 58 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)
    36.2 s ± 103 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)



```python
# this time tokenizing lists - looks the same!
%timeit test_dump(list_pars,DevinToks)
%timeit test_dump(list_pars,pickle)
%timeit test_dump(list_pars,_pickle)
%timeit test_dump(list_pars,json)
```

    92 ms ± 185 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
    5.49 ms ± 269 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    5.41 ms ± 212 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    31.2 ms ± 36.7 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)



```python
# now test loading
pdat, cdat, jdat, ddat = test_dump(paragraphs,pickle), test_dump(paragraphs,_pickle), test_dump(paragraphs,json), test_dump(paragraphs,DevinToks)
print(len(pdat), len(cdat), len(jdat), len(ddat))

def test_load(dat, serializer):
    return serializer.loads(dat)
%timeit test_load(ddat,DevinToks)
%timeit test_load(pdat,pickle)
%timeit test_load(cdat,_pickle)
%timeit test_load(jdat,json)
```

    470069266 470069266 4020020000 3410010001



```python
fnames = ('pic.dat', 'cpic.dat', 'json.dat', 'devin.dat')
```


```python
a = np.zeros((10000,1000))
%timeit a.tobytes()
%timeit pickle.dumps(a)
%timeit _pickle.dumps(a)
bdat, pdat, cdat = a.tobytes(), pickle.dumps(a), _pickle.dumps(a)
len(bdat), len(pdat), len(cdat)
```


```python
%timeit np.frombuffer(bdat)
%timeit pickle.loads(pdat)
%timeit _pickle.loads(cdat)
```


```python

```
