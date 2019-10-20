```python
import random
def rr(a,b):
    return range(random.randrange(a,b))
```


```python
tok_mark = '\x1f' # unit separator
storechars = (
    '\x1c', # file separator
    '\x1d', # group separator
    '\x1e', # record separator
    '\x0b', # vertical tab
)
def printhex(s):
    return ''.join(
        "\\x{:02x} ".format(ord(c)) if c in storechars or c == tok_mark else c
        for c in s
    )
#printhex('\x1da\x1fb\x1f\x1da\x1f\x1d\x1d\x1dc\x1f\x1d\x1c')
```


```python
def store(toktree, sep, i=0):
    if isinstance(toktree,str):
        print('    '*i, 'token', toktree, '({:02x})'.format(ord(tok_mark)))
        return toktree + tok_mark
    
    print('    '*i, toktree, '({:02x})'.format(ord(sep[i])))
    return ''.join(
        store(child, sep, i+1)
        for child in toktree
    ) + sep[i]


#s = (('d','e','f',),),(('a','b'),('a',),(),(),('c',))
#chars = store(s, storechars)
#load(chars, storechars)

s = [[[['a'],['b']]]]
chars = store(s, storechars)
print(printhex(chars))
load(chars, storechars)
```

     [[[['a'], ['b']]]] (1c)
         [[['a'], ['b']]] (1d)
             [['a'], ['b']] (1e)
                 ['a'] (0b)
                     token a (1f)
                 ['b'] (0b)
                     token b (1f)
    a\x1f \x0b b\x1f \x0b \x1e \x1d \x1c 





    (((('a',), ('b',)),),)




```python
def load_l(treestr, sep, i=0):
    #print('  '*(i) + printhex(treestr), '({:02x})'.format(ord(sep[i])))
    if not treestr:
        return ()
    elif treestr[-1] == tok_mark:
        return tuple(treestr[:-1].split(tok_mark))
    children = treestr.split(sep[i])[:-1]
    return tuple(load_l(child, sep, i+1) for child in children)

def load(treestr, sep):
    return load_l(treestr, sep, i=0)[0]
```


```python
s = tuple(tuple(str(i) for i in rr(0,10)) for _ in rr(100,1000))
print(len(s))
%timeit store(s, storechars)
```


```python
s = tuple(tuple(str(i) for i in rr(100,1000)) for _ in rr(1000,10000))
chars = store(s, storechars)
senlen = [len(sx) for sx in s]
print(len(s), sum(senlen)/len(senlen))
%timeit load(chars, storechars)
```


```python

```


```python
s = ((),('a','b'),('a',),(),(),('c',))
chars = store(s, sep)
load(chars, storechars)
```
