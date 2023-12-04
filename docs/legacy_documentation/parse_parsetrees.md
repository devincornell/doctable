# Working with doctable Parsetrees
Here I'll show you how to extract and use parsetrees in your doctable using Spacy + doctable. The motivation is that parsetree information in raw Spacy Document objects are very large and not suitable for storage when using large corpora. We solve this by simply converting the Spacy Document object to a tree data structure built from python lists and dictionaries, and use the `ParseTree` object to serialize, de-serialize, and interact with the tree structure.

We use this feature using the `get_parsetrees` pipeline component after the spacy parser. [Check the docs](ref/doctable.parse.html) to learn more about this function. You can see more examples of creating parse pipelines in our [overview examples](examples/parse_basics.html).


```python
import spacy
nlp = spacy.load('en_core_web_sm')
import pandas as pd
import sys
sys.path.append('..')
import doctable
```

First we define some example text docuemnts, Star Wars themed.


```python
text = 'Help me Obi-Wan Kenobi. You’re my only hope. ' \
    'I find your lack of faith disturbing. ' \
    'Do, or do not - there is no try. '
text
```




    'Help me Obi-Wan Kenobi. You’re my only hope. I find your lack of faith disturbing. Do, or do not - there is no try. '



## Creating `ParseTreeDoc` Objects

The most direct way of creating a parsetree is to parse the desired text using the spacy language model, then use `ParseTreeDoc.from_spacy()` to construct the `ParseTreeDoc`. The `ParseTreeDoc` object is a container for parsetree objects representing each of the sentences identified with the SpaCy parser.


```python
spacydoc = nlp(text)
doc = doctable.ParseTreeDoc.from_spacy(spacydoc)
print(f'{len(doc)} sentences of type {type(doc)}')
```

    4 sentences of type <class 'doctable.parse.documents.parsetreedoc.ParseTreeDoc'>


The most important arguments to `parse_tok_func` are `text_parse_func` and `userdata_map`.

1. `text_parse_func` determines the mapping from a spacy doc object to the text representation of each token accessed through `token.text`. By default this parameter is set to `lambda d: d.text`.

2. `userdata_map` is a dictionary mapping an attribute name to a function. You can, for instance, extract info from the original spacy doc object through this method. I'll explain later how these attributes can be accessed and used.


```python
doc = doctable.ParseTreeDoc.from_spacy(spacydoc, 
    text_parse_func=lambda spacydoc: spacydoc.text,
    userdata_map = {
        'lower': lambda spacydoc: spacydoc.text.lower().strip(),
        'lemma': lambda spacydoc: spacydoc.lemma_,
        'like_num': lambda spacydoc: spacydoc.like_num,
    }
)
print(doc[0]) # show the first sentence
```

    ParseTree(Help me Obi - Wan Kenobi .)


## Working With `ParseTree`s

`ParseTreeDoc` objects represent sequences of `ParseTree` objects identified by the spacy language parser. You can see we can access individual sentence parsetrees using numerical indexing or through iteration.


```python
print(doc[0])
for sent in doc:
    print(sent)
```

    ParseTree(Help me Obi - Wan Kenobi .)
    ParseTree(Help me Obi - Wan Kenobi .)
    ParseTree(You ’re my only hope .)
    ParseTree(I find your lack of faith disturbing .)
    ParseTree(Do , or do not - there is no try .)


Now we will show how to work with `ParseTree` objects. These objects are collections of tokens that can be accessed either as a tree (based on the structure of the dependency tree produced by spacy), or as an ordered sequence. We can use numerical indexing or iteration to interact with individual tokens.


```python
for token in doc[0]:
    print(token)
```

    Help
    me
    Obi
    -
    Wan
    Kenobi
    .


We can work with the tree structure of a `ParseTree` object using the `root` property.


```python
print(doc[0].root)
```

    Help


And access the children of a given token using the `childs` property. The following tokens are children of the root token.


```python
for child in doc[0].root.childs:
    print(child)
```

    me
    Kenobi
    .


These objects can be serialized using the `.as_dict()` method and de-serialized using the `.from_dict()` method.


```python
serialized = doc.as_dict()
deserialized = doctable.ParseTreeDoc.from_dict(serialized)
for sent in deserialized:
    print(sent)
```

    ParseTree(Help me Obi - Wan Kenobi .)
    ParseTree(You ’re my only hope .)
    ParseTree(I find your lack of faith disturbing .)
    ParseTree(Do , or do not - there is no try .)


## More About `Token`s
Each token in a `ParseTree` is represented by a `Token` object. These objects maintain the tree structure of a parsetree, and each node contains some default information as well as optional and custom information. These are the most important member variables:

#### Member Variables
+ _i_: index of token in sentence
+ _text_: text representation of token
+ _tag_: the part-of-speech tag offered by the dependency parser (different from POS tagger)
+ _dep_: the dependency relation to parent object. See the [Spacy annotation docs](https://spacy.io/api/annotation#dependency-parsing) for more detail.
+ _parent_: reference to parent node
+ _childs_: list of references to child nodes

#### Optional Member Variables
The following are provided if the associated spacy parser component was enabled.

+ _pos_: part-of-speech tag created if user enablled POS 'tagger' in Spacy. See [Spacy POS tag docs](https://spacy.io/api/annotation#pos-tagging) for more detail. Also check out docs for [UPOS tags](https://universaldependencies.org/docs/u/pos/).
+ _ent_: named entity type of token (if NER was enabled when creating parsetree). See [Spacy NER docs](https://spacy.io/api/annotation#named-entities) for more detail.


```python
for tok in doc[0][:3]:
    print(f"{tok.text}:\n\ti={tok.i}\n\ttag={tok.tag}\n\tdep={tok.dep}\n\tent={tok.ent}\n\tpos={tok.pos}")
```

    Help:
    	i=0
    	tag=VB
    	dep=ROOT
    	ent=
    	pos=VERB
    me:
    	i=1
    	tag=PRP
    	dep=dobj
    	ent=
    	pos=PRON
    Obi:
    	i=2
    	tag=NNP
    	dep=compound
    	ent=
    	pos=PROPN


We can also access the custom token properties provided to the `ParseTreeDoc.from_spacy()` method earlier.


```python
for token in doc[0]:
    print(f"{token.text}: {token['lemma']}")
```

    Help: help
    me: I
    Obi: Obi
    -: -
    Wan: Wan
    Kenobi: Kenobi
    .: .


## Recursive Functions on Parsetrees

We can also navigate the tree structure of parsetrees using recursive functions. Here I simply print out the trajectory of this recursive function.


```python
def print_recursion(tok, level=0):
    if not tok.childs:
        print('    '*level + 'base node', tok)
    else:
        print('    '*level + 'entering', tok)
        for child in tok.childs:
            print_recursion(child, level+1)
        print('    '*level + 'leaving', tok)

print_recursion(doc[0].root)
```

    entering Help
        base node me
        entering Kenobi
            entering Wan
                base node Obi
                base node -
            leaving Wan
        leaving Kenobi
        base node .
    leaving Help


## Create Using `ParsePipeline`s
The most common use case, however, probably involves the creation of of a `ParsePipeline` in which the end result will be a `ParseTreeDoc`. We make this using the `get_parsetrees` pipeline component, and here we show several of the possible arguments.



```python
parser = doctable.ParsePipeline([
    nlp, # the spacy parser
    doctable.Comp('get_parsetrees', **{
        'text_parse_func': lambda spacydoc: spacydoc.text,
        'userdata_map': {
            'lower': lambda spacydoc: spacydoc.text.lower().strip(),
            'lemma': lambda spacydoc: spacydoc.lemma_,
            'like_num': lambda spacydoc: spacydoc.like_num,
        }
    })
])
parser.components
```




    [<spacy.lang.en.English at 0x7f3d584c7dc0>,
     functools.partial(<function get_parsetrees at 0x7f3d27b95dc0>, text_parse_func=<function <lambda> at 0x7f3d26a17a60>, userdata_map={'lower': <function <lambda> at 0x7f3d26a17160>, 'lemma': <function <lambda> at 0x7f3d26a170d0>, 'like_num': <function <lambda> at 0x7f3d26a17040>})]



You can see that the parser provides the same output as we got before with `ParseTreeDoc.from_spacy()`.


```python
for sent in parser.parse(text):
    print(sent)
```

    ParseTree(Help me Obi - Wan Kenobi .)
    ParseTree(You ’re my only hope .)
    ParseTree(I find your lack of faith disturbing .)
    ParseTree(Do , or do not - there is no try .)
