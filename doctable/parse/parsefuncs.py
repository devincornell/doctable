''' These functions are used as wrappers around SpaCy parsers, and can be used
either standalone or as part of a doctable.ParsePipeline.

The two primary parse functions here are `tokenize` and `get_parsetrees`.
Use `tokenize` when you want to extract lists of tokens (split by sentence
or not) and `get_parsetrees` when you'd like to extract condensed versions
of SpaCy parsetrees.

The `tokenize` function accepts two parameters, `keep_tok_func` and 
`parse_tok_func`, which can be custom or optionally filled by 
`keep_tok` and `parse_tok`. These methods are also registered as 
components in `doctable.ParsePipeline`, so can be accessed using 
`doctable.Comp()` as shown below.

```
# add pipeline components
parser = doctable.ParsePipeline([
    spacy.load('en'), # first run spacy parser
    doctable.Comp('tokenize', **{
        'split_sents': False,
        'keep_tok_func': doctable.Comp('keep_tok'),
        'parse_tok_func': doctable.Comp('parse_tok'),
    })
])
```

A more complete `ParsePipeline` example might look like the code below.
This example uses the `merge_tok_spans` function to merge named entities as
single tokens in SpaCy then uses the `tokenize` function in conjunction 
with `keep_tok` (which drops whitespace tokens but keeps punctuation and 
stopwords) and `parse_tok` (which capitalizes named entities, replaces 
numbers with "NUM", and does not lemmatize tokens).

```
parser = doctable.ParsePipeline([
    spacy.load('en'), # spacy nlp parser object
    
    # merge spacy multi-word named entities (doctable.parse.merge_tok_spans)
    Comp('merge_tok_spans', merge_ents=True, merge_noun_chunks=False),
    
    # tokenize document
    Comp('tokenize', **{
        'split_sents': False,
        
        # choose tokens to keep (doctable.parse.keep_tok)
        'keep_tok_func': Comp('keep_tok', **{
            'keep_whitespace': False, # don't keep whitespace
            'keep_punct': True, # keep punctuation and stopwords
            'keep_stop': True,
        }),
        
        # choose how to convert Spacy token t text (doctable.parse.parse_tok)
        'parse_tok_func': Comp('parse_tok', **{
            'format_ents': True,
            'lemmatize': False,
            'num_replacement': 'NUM',
            'ent_convert': lambda e: e.text.upper(), # function to capitalize named entities
        })
    })
])
```


'''


from doctable.documents.parsetreedoc import ParseTreeDoc
import re

#from .parsetree import ParseTree

# xml for removing stuff    
re_url = re.compile(r'http\S+', flags=re.MULTILINE)
re_xml_tag = re.compile(r'<[^<]+>', flags=re.MULTILINE)
re_digits = re.compile(r"\d*[-\./,]*\d+")

def preprocess(text, replace_url=None, replace_xml=None, replace_digits=None):
    ''' A few useful preprocessing functions for raw text.
    Args:
        text (str): document as a text string
        replace_url (str or None): if not None, replace url with string
        replace_xml (str or None): if not None, replace xml tags with string
        replace_digits (str or None): if not None, replace digits with string
    '''
    
    if replace_url is not None:
        text = re.sub(re_url, replace_url, text)
        
    if replace_xml is not None:
        text = re.sub(re_xml_tag, replace_xml, text)
        
    if replace_digits is not None:
        text = re.sub(re_digits, replace_digits, text)
        
    return text


def identity(x):
    return x

def tokenize(doc, split_sents=True, keep_tok_func=None, parse_tok_func=None):
    ''' Convert spacy doc into a series of tokens (as sentences or not).
    Args:
        split_sents (bool): parse into list of sentence tokens using doc.sents.
        merge_ents (bool): merge multi_word entities into same token.
        ngrams (iter<iter<str>>): iterable of token tuples to merge after parsing.
        spacy_ngram_matcher (spacy Matcher): matcher object to use on the spacy doc.
            Normally will create using spacy.Matcher(nlp.vocab), see more details
            at https://spacy.io/usage/rule-based-matching And also note that the 
            nlp object must be the one used for parsing.
        keep_tok_func (func): func used to decide to keep func or not. Default is
            identity function
        parse_tok_func (func): func used to parse tokens. By default uses 
            identify function.
    '''
                    
    if parse_tok_func is None:
        parse_tok_func = identity
    if keep_tok_func is None:
        keep_tok_func = identity
        
    # sentence parsing mode
    if split_sents:
        sents = [
            [parse_tok_func(tok) 
             for tok in sent if keep_tok_func(tok)] 
            for sent in doc.sents
        ]
        
        return sents
    
    # doc parsing mode
    else:
        toks = [parse_tok_func(tok) 
                for tok in doc if keep_tok_func(tok)]
        
        return toks


def parse_tok(tok, num_replacement=None, digit_replacement=None, lemmatize=False, normal_tok_parse=None, 
        format_ents=False, ent_convert=None):
    '''Convert spacy token object to string.
    Args:
        tok (spacy token or span): token object to convert to string.
        replace_num (str/None): Replace number following tok.like_num (includes "five", 
            or 5) with a special token (i.e. __NUM__). None means no replacement.
        replace_digit (str/None): Replace digit meeting tok.is_digit with special token. 
            Only used when replace_num is None.
        lemmatize (bool): return lemma instead of full word.
        normal_convert (func): custom conversion function to happen as last step
            for non-entities. This way can keep all other functionality.
        format_ents (bool): Replace whitespace with space and capitalize first 
            letter of ents.
        ent_convert (func): custom conversion function to happen as last step
            for entities. This way can keep all other functionality.
    '''
    
    # catch issues with 
    
    # replace  numbers
    if num_replacement is not None and tok.like_num:
        return num_replacement
    if digit_replacement is not None and tok.is_digit:
        return digit_replacement
    
    if tok.ent_type_ == '': # non-entity token
        if normal_tok_parse is not None:
            normal_tok_parse(tok)
        else:
            if lemmatize:
                return tok.lemma_.lower().strip()
            else:
                return tok.text.lower().strip()
    
    else: # token is entity
        if ent_convert is not None:
            return ent_convert(tok)
        elif format_ents:
            return ' '.join(tok.text.split()).title()
        else:
            return tok.text.strip()




def keep_tok(tok, keep_whitespace=False, keep_punct=True, keep_stop=True, keep_digit=True, 
               keep_num=True, keep_ents=True, keep_ent_types=None, rm_ent_types=None, 
               keep_pos=None, rm_pos=None, addtnl_func=None):
    ''' Decide to use token or not (can be overridden).
    Args:
        keep_whitespace (bool): keep all-whitespace tokens.
        keep_punct (bool): keep punctuation.
        keep_stop (bool): keep stopwords.
        keep_num (bool): keep numbers using tok.is_num.
        keep_digit (bool): keep digits using tok.is_digit.
        keep_ents (bool): keep named entities
        keep_ent_types (list<str>): keep only these entity types
        rm_ent_types (list<str>): remove these entity types
        keep_pos (list<str>): keep only toks with these POS
        rm_pos (list<str>): remove toks with these POS
        addtnl_func (func): additional custom criteria to meet
    Returns:
        True if token should be kept.
    '''
    
    
    if not keep_whitespace and (tok.is_space or len(tok.text.strip()) == 0):
        return False
    
    if not keep_punct and tok.is_punct:
        return False
    
    if not keep_stop and tok.is_stop:
        return False
    
    if not keep_num and tok.like_num:
        return False
    
    if not keep_digit and tok.is_digit:
        return False
    
    if keep_pos is not None and tok.pos_ not in keep_pos:
        return False
    
    elif rm_pos is not None and tok.pos_ in rm_pos:
        return False
    
    if tok.ent_type_ != '': # if token is named entity
        
        if not keep_ents: # remove the named entity
            return False
    
        if keep_ent_types is not None and tok.ent_type_ not in keep_ent_types:
            return False
    
        elif rm_ent_types is not None and tok.ent_type_ in rm_ent_types:
            return False
        
    # if all other criteria has been met, apply this one last check
    if addtnl_func is not None:
        return addtnl_func(tok)
    
    return True
        



def merge_tok_spans(doc, merge_ents=True, spacy_ngram_matcher=None, merge_noun_chunks=False):
    ''' Apply merges to doc object including entities, normal ngrams, and noun chunks.
    Args:
        doc (Spacy Doc object): doc to merge spans in
        merge_ents (bool): combine multi-word entities using spacy doc.retokenize()
        spacy_ngram_matcher (spacy Matcher object): rule-based matching object for 
            ngrams in Spacy. See https://spacy.io/usage/rule-based-matching
        merge_noun_chunks (bool): automatically merge noun chunks
    '''
    if spacy_ngram_matcher is not None:
        # merge custom matches
        with doc.retokenize() as retokenizer:
            for match_id, start, end in spacy_ngram_matcher(doc):
                retokenizer.merge(doc[start:end])
    if merge_ents:
        # merge entities
        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                retokenizer.merge(ent)
    if merge_noun_chunks:
        # merge entities
        with doc.retokenize() as retokenizer:
            for nc in doc.noun_chunks:
                retokenizer.merge(nc)
    return doc # just in case user tries to assign




def merge_tok_ngrams(toks, ngrams=tuple(), ngram_sep='_'):
    '''Merges manually specified consecutive tokens into single tokens.
    Args:
        toks (list<str>): token list through which to search for ngrams.
        ngrams (list<list<str>>): list of ngrams (as sequence of str) to 
            combine into single tokens.
        ngram_sep (str): string to join ngram parts with.
    '''
    new_toks = list()
    ngram_starts = [ng[0] for ng in ngrams] # first word of every ngram
    i = 0
    while i < len(toks):
        if toks[i] in ngram_starts: # match is possible
            found_match = False
            for ng in ngrams:
                zip_rng = zip(range(len(ng)), range(i,len(toks)))
                if all([ng[j]==toks[k] for j,k in zip_rng]):
                    new_toks.append(ngram_sep.join(ng))
                    i += len(ng)
                    found_match = True
                    break
            if not found_match:
                new_toks.append(toks[i])
                i += 1
        else: # match is impossible
            new_toks.append(toks[i])
            i += 1
    return new_toks




def get_parsetrees(doc, text_parse_func=lambda stok: stok.text, userdata_map=dict()):
    '''Extracts parsetree from spacy doc objects.
    Args:
        doc (spacy.Doc object): doc to generate parsetree from.
        parse_tok_func (func<spacy.Token, str>): function used to convert token to 
            a string representation. Usually a lambda function 
            wrapping some variant of self.parse_tok().
        userdata_map (dict<str->func>): attribute to function 
            mapping. Functions take a token and output a property
            that will be stored in each parsetree node.
    '''
    return ParseTreeDoc.from_spacy(doc, text_parse_func=text_parse_func, 
                            userdata_map=userdata_map)
    #sent_trees = [
    #    ParseTree(sent.root, text_parse_func=text_parse_func, userdata_map=userdata_map)
    #    for sent in doc.sents
    #]
    #return sent_trees





    