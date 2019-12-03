import re
from multiprocessing import Pool
import math
import os

from .parsetree import ParseTree

class DocParser:
    '''Class that maintains convenient functions for parsing Spacy doc objects.'''
    
    re_url = re.compile(r'http\S+', flags=re.MULTILINE)
    
    
    @classmethod
    def distribute_parse(cls, texts, spacynlp, parsefunc=None, preprocessfunc=None, 
        paragraph_sep=None, n_cores=None, verbose=False):
        '''Will distribute document parsing tasks across multiple processors.
        Args:
            texts (list<str>): list of document strings to parse
            spacynlp (spacy Lanugage model): i.e. nlp = spacy.load('en')
            parsefunc (func): function accepting a single spacy doc object
                as an argument, and ouputting the desired parsed document.
                Defaults to DocParser.tokenize_doc() with defaults
            preprocessfunc (func): function used to process text before parsing
                with spacy.
            paragraph_sep (str or None): used to separate documents into 
                paragraphs before parsing with spacy if needed. This will 
                distribute paragraph parsing across processes which is more
                balanced than distributing at document level.
        '''
        if parsefunc is None:
            parsefunc = cls.tokenize_doc
        
        if preprocessfunc is None:
            preprocessfunc = cls.preprocess
            
        # split into paragraphs
        if verbose: print('parsing {} docs'.format(len(texts)))
        if paragraph_sep is not None:
            texts, ind = list(zip(*[(par.strip(),i) for i,text in enumerate(texts) 
                              for par in text.split(paragraph_sep)]))
            if verbose: print('split into {} paragraphs'.format(len(texts)))
                
        # decide on number of cores
        if n_cores is None:
            n_cores = min([os.cpu_count(), len(texts)])
        else:
            n_cores = min([os.cpu_count(), len(texts), n_cores])
                
                
        # start parallel processing. Keep inside Pool() to get number of used processes
        with Pool(processes=n_cores) as p:
            chunk_size = math.ceil(len(texts)/p._processes)
            print('processing chunks of size {} with {} processes.'.format(chunk_size,p._processes))
            
            chunks = [(texts[i*chunk_size:(i+1)*chunk_size], spacynlp, parsefunc, preprocessfunc)
                           for i in range(p._processes)]

            parsed = [d for docs in p.map(cls._distribute_parse_thread, chunks) 
                    for d in docs]
            print('returned {} parsed docs or paragraphs'.format(len(parsed)))
            
            if paragraph_sep is None:
                parsed_docs = parsed
            else:
                parsed_docs = list()
                last_i, last_ind = 0, 0
                for i in range(len(ind)):
                    if ind[i] != last_ind or i == len(ind)-1:
                        parsed_docs.append(parsed[last_i:i])
                        last_ind = ind[i]
                        last_i = i
        
        return parsed_docs
    
    
    @staticmethod
    def _distribute_parse_thread(args):
        texts, nlp, parsefunc, preprocessfunc = args
        parsed_docs = list()
        for doc in nlp.pipe(map(preprocessfunc,texts)):
            parsed_docs.append(parsefunc(doc))
        return parsed_docs
        
    
    
    @classmethod
    def get_parsetrees(cls, doc, tok_parse_func=None, info_func_map=dict(), merge_ents=False, 
            spacy_ngram_matcher=None, merge_noun_chunks=False):
        '''Extracts parsetree from spacy doc objects.
        Args:
            doc (spacy.Doc object): doc to generate parsetree from.
            tok_parse_func (func): function used to convert token to 
                a string representation. Usually a lambda function 
                wrapping some variant of self.parse_tok().
            info_func_map (dict<str->func>): attribute to function 
                mapping. Functions take a token and output a property
                that will be stored in each parsetree node.
            merge_ents (bool): merge multi-word entities.
            spacy_ngram_matcher (Spacy Matcher): used to create ngrams
                with Spacy. Powerful wildcards etc.
            merge_noun_chunks (bool): merge noun chunks or not.
        '''
        if tok_parse_func is None:
            tok_parse_func = cls.parse_tok
        
        # apply ngram merges to doc object (permanently modifies doc object)
        cls.apply_ngram_merges(
            doc, 
            merge_ents=merge_ents, 
            spacy_ngram_matcher=spacy_ngram_matcher, 
            merge_noun_chunks=merge_noun_chunks
        )
        
        sent_trees = [
            ParseTree(sent.root, tok_parse_func, info_func_map=info_func_map)
            for sent in doc.sents
        ]
        return sent_trees
        
    
    @classmethod
    def tokenize_doc(cls, doc, split_sents=False, merge_ents=False, merge_noun_chunks=False, 
        ngrams=list(), spacy_ngram_matcher=None, ngram_sep=' ', use_tok_args=dict(), 
        parse_tok_args=dict()):
        '''Parse spacy doc object.
        Args:
            split_sents (bool): parse into list of sentence tokens using doc.sents.
            merge_ents (bool): merge multi_word entities into same token.
            ngrams (iter<iter<str>>): iterable of token tuples to merge after parsing.
            spacy_ngram_matcher (spacy Matcher): matcher object to use on the spacy doc.
                Normally will create using spacy.Matcher(nlp.vocab), see more details
                at https://spacy.io/usage/rule-based-matching And also note that the 
                nlp object must be the one used for parsing.
            use_tok_args (dict): arguments to be passed to .use_tok()
            parse_tok_args (dict): arguments to pass to .parse_tok()
        '''
        
        # NOTE! These need to be under two separate retokenize() blocks
        #     because retokenizing only occurs after the block and sometimes
        #     custom matches (provided via matcher) overlap with ents. Easiest
        #     way is to do custom first, then non-overlapping.
        cls.apply_ngram_merges(doc, 
                merge_ents=merge_ents, 
                spacy_ngram_matcher=spacy_ngram_matcher,
                merge_noun_chunks=merge_noun_chunks
            )
                
        # sentence parsing mode
        if split_sents:
            sents = [
                [cls.parse_tok(tok, **parse_tok_args) 
                 for tok in sent if cls.use_tok(tok, **use_tok_args)] 
                for sent in doc.sents
            ]
            
            if len(ngrams) > 0:
                sents = [cls.merge_ngrams(sent, ngrams, ngram_sep=ngram_sep) for sent in sents]
            
            return sents
        
        # doc parsing mode
        else:
            toks = [cls.parse_tok(tok, **parse_tok_args) 
                    for tok in doc if cls.use_tok(tok, **use_tok_args)]
            
            if len(ngrams) > 0:
                toks = cls.merge_ngrams(toks, ngrams, ngram_sep=ngram_sep)
            return toks
        
    @staticmethod
    def parse_tok(tok, replace_num=None, replace_digit=None, lemmatize=False, normal_convert=None, 
            format_ents=True, ent_convert=None):
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
        
        # replace characters
        if replace_digit is not None and tok.is_digit:
            return replace_digit
        if replace_num is not None and tok.like_num:
            return replace_num
        
        if tok.ent_type_ == '': # non-entity token
            if lemmatize:
                return tok.lemma_.lower().strip()
            elif normal_convert is not None:
                return normal_convert(tok)
            else:
                return tok.text.lower().strip()
        
        else: # token is entity
            if ent_convert is not None:
                return ent_convert(tok)
            elif format_ents:
                return ' '.join([t.lower().capitalize() for t in tok.text.split()])
            else:
                return tok.text.strip()
        
    @staticmethod
    def use_tok(tok, filter_whitespace=True, filter_punct=False, filter_stop=False, filter_digit=False, filter_num=False, filter_all_ents=False, filter_ent_types=tuple()):
        '''Decide to use token or not (can be overridden).
        Args:
            no_whitespace (bool): exclude whitespace.
            no_punct (bool): exclude punctuation.
            no_num (bool): exclude numbers using tok.is_num.
            no_digit (bool): exclude digits using tok.is_digit.
            no_stop (bool): exclude stopwords.
        '''
        do_use_tok = True
        if filter_whitespace:
            do_use_tok = do_use_tok and (not tok.is_space and len(tok.text.strip()) > 0)
        
        if filter_punct:
            do_use_tok = do_use_tok and not tok.is_punct
            
        if filter_stop:
            do_use_tok = do_use_tok and not tok.is_stop
            
        if filter_digit:
            do_use_tok = do_use_tok and not tok.is_digit
            
        if filter_num:
            do_use_tok = do_use_tok and not tok.like_num
        
        if filter_all_ents:
            do_use_tok = do_use_tok and tok.ent_type_ == ''
            
        if len(filter_ent_types) > 0:
            do_use_tok = do_use_tok and tok.ent_type_ not in filter_ent_types
            
        return do_use_tok
    
    @classmethod
    def preprocess(cls, text, remove_url=False):
        '''Apply preprocessing step before parsing.
        Args:
            text (str): document as a text string
            remove_url (bool): choose to remove url
        '''
        if remove_url:
            text = re.sub(cls.re_url, '', text)
        return text
    
    @staticmethod
    def apply_ngram_merges(doc, merge_ents=True, spacy_ngram_matcher=None, merge_noun_chunks=False):
        '''Apply merges to doc object including entities, normal ngrams, and noun chunks.'''
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
    
    @staticmethod
    def merge_ngrams(toks, ngrams, ngram_sep=' '):
        '''Merges consecutive strings (tokenized n-grams) into single tokens.
        '''
        new_toks = list()
        ngram_starts = [ng[0] for ng in ngrams] # first word of every ngram
        i = 0
        while i < len(toks):
            if toks[i] in ngram_starts: # match is possible
                for ng in ngrams:
                    zip_rng = zip(range(len(ng)), range(i,len(toks)))
                    if all([ng[j]==toks[k] for j,k in zip_rng]):
                        new_toks.append(ngram_sep.join(ng))
                        i += len(ng)
                        break
                new_toks.append(toks[i])
                i += 1
            else: # match is impossible
                new_toks.append(toks[i])
                i += 1
        return new_toks
        


        
        
        