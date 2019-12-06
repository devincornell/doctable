import re
from multiprocessing import Pool
import math
import os

from .parsetree import ParseTree

class DocParser:
    '''Class that maintains convenient functions for parsing Spacy doc objects.'''
    
    re_url = re.compile(r'http\S+', flags=re.MULTILINE)
    re_xml_tag = re.compile('<[^<]+>', flags=re.MULTILINE)
    re_digits = re.compile("\d*[-\./,]*\d+")
    
    @classmethod
    def preprocess(cls, text, replace_url=None, replace_xml=None, replace_digits=None):
        '''Apply preprocessing step, modifies and returns text.
        Args:
            text (str): document as a text string
            replace_url (str or None): if not None, replace url with string
            replace_xml (str or None): if not None, replace xml tags with string
            replace_digits (str or None): if not None, replace digits with string
        '''
        
        if replace_url is not None:
            text = re.sub(cls.re_url, replace_url, text)
            
        if replace_xml is not None:
            text = re.sub(cls.re_xml_tag, replace_xml, text)
            
        if replace_digits is not None:
            text = re.sub(cls.re_digits, replace_digits, text)
            
        return text
    
    @classmethod
    def distribute_parse_insert(cls, texts, spacynlp, dt_inst, parse_func, n_cores):
        '''Distributes document parsing to eventually store in doctable.
        Args:
            texts (list<str>): list of texts to parse
            spacynlp (spacy parser object): parser object applied to texts
            dt_inst (DocTable): doctable instance to insert docs into
            parse_func (fun): function to take raw text and insert into doctable.
        Returns:
            None
        '''
    
    

            
    
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
                
        # decide on number of cores
        if n_cores is None:
            n_cores = min([os.cpu_count(), len(texts)])
        else:
            n_cores = min([os.cpu_count(), len(texts), n_cores])
                
        # start parallel processing. Keep inside Pool() to get number of used processes
        with Pool(processes=n_cores) as p:
            chunk_size = math.ceil(len(texts)/p._processes)
            if verbose: print('processing chunks of size {} with {} processes.'.format(chunk_size,p._processes))
            
            chunks = [(texts[i*chunk_size:(i+1)*chunk_size], spacynlp, parsefunc, preprocessfunc)
                           for i in range(p._processes)]

            parsed = [d for docs in p.map(cls._distribute_parse_thread, chunks) 
                    for d in docs]
            if verbose: print('returned {} parsed docs or paragraphs'.format(len(parsed)))            
            
            if paragraph_sep is None:
                parsed_docs = parsed
            else:
                parsed_docs = list()
                last_i, last_ind = 0, 0
                for i in range(len(ind)):
                    if ind[i] != last_ind:
                        parsed_docs.append(parsed[last_i:i])
                        last_ind = ind[i]
                        last_i = i
                    elif i == len(ind)-1:
                        parsed_docs.append(parsed[last_i:])
        
        return parsed_docs
    
    @staticmethod
    def _distribute_parse_thread(args):
        texts, nlp, parsefunc, preprocessfunc = args
        parsed_docs = list()
        for doc in nlp.pipe(map(preprocessfunc,texts)):
            parsed_docs.append(parsefunc(doc))
        return parsed_docs
        
    
    
    @classmethod
    def get_parsetrees(cls, doc, parse_tok_func=None, info_func_map=dict(), merge_ents=False, 
            spacy_ngram_matcher=None, merge_noun_chunks=False):
        '''Extracts parsetree from spacy doc objects.
        Args:
            doc (spacy.Doc object): doc to generate parsetree from.
            parse_tok_func (func): function used to convert token to 
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
        if parse_tok_func is None:
            parse_tok_func = cls.parse_tok
        
        # apply ngram merges to doc object (permanently modifies doc object)
        cls.apply_ngram_merges(
            doc, 
            merge_ents=merge_ents, 
            spacy_ngram_matcher=spacy_ngram_matcher, 
            merge_noun_chunks=merge_noun_chunks
        )
        
        sent_trees = [
            ParseTree(sent.root, parse_tok_func, info_func_map=info_func_map)
            for sent in doc.sents
        ]
        return sent_trees
        
    
    @classmethod
    def tokenize_doc(cls, doc, split_sents=False, merge_ents=False, merge_noun_chunks=False, 
        ngrams=list(), spacy_ngram_matcher=None, ngram_sep=' ', use_tok_func=None, 
        parse_tok_func=None):
        '''Parse spacy doc object.
        Args:
            split_sents (bool): parse into list of sentence tokens using doc.sents.
            merge_ents (bool): merge multi_word entities into same token.
            ngrams (iter<iter<str>>): iterable of token tuples to merge after parsing.
            spacy_ngram_matcher (spacy Matcher): matcher object to use on the spacy doc.
                Normally will create using spacy.Matcher(nlp.vocab), see more details
                at https://spacy.io/usage/rule-based-matching And also note that the 
                nlp object must be the one used for parsing.
            use_tok_func (func): func used to decide to keep func or not. Default is
                cls.use_tok().
            parse_tok_func (func): func used to parse tokens. By default uses 
                cls.parse_tok().
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
                
            
        if parse_tok_func is None:
            parse_tok_func = cls.parse_tok
        if use_tok_func is None:
            use_tok_func = cls.use_tok
            
        # sentence parsing mode
        if split_sents:
            sents = [
                [parse_tok_func(tok) 
                 for tok in sent if use_tok_func(tok)] 
                for sent in doc.sents
            ]
            
            if len(ngrams) > 0:
                sents = [cls.merge_ngrams(sent, ngrams, ngram_sep=ngram_sep) for sent in sents]
            
            return sents
        
        # doc parsing mode
        else:
            toks = [parse_tok_func(tok) 
                    for tok in doc if use_tok_func(tok)]
            
            if len(ngrams) > 0:
                toks = cls.merge_ngrams(toks, ngrams, ngram_sep=ngram_sep)
            return toks
        
    @staticmethod
    def parse_tok(tok, replace_num=None, replace_digit=None, lemmatize=False, normal_convert=None, 
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
        '''Merges specified consecutive tokens into single tokens.
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
    
    
    #################### DISTRIBUTED PARSING/STORING METHODS #######################
    
    @classmethod
    def _distribute_chunk_process_store(cls, elements, parse_func, dt_inst, 
                                        *parse_static_args,n_cores=None):
        '''Distributes parse_func to store in dt_inst across multiple processes.
        Description: This method is needed so it can maintain a separate db connection
            in each process. Be sure to set timeout in DocTable constructor using
            connect_args={'timeout': timeout}, where timeout is a large number 
            (in seconds). Large enough that it can wait for other processes to 
            insert before inserting.
        '''
        
        # close conn to reconnect in thread
        conn_was_open = dt_inst._conn is not None
        dt_inst.close_engine()
        
        # wrap dt_inst into elements for extraction in _distribute_chunk_process_store_thread
        #elements = [(el,'shit') for el in elements]
        res = cls._distribute_chunk_process(elements, parse_func, dt_inst, 
            *parse_static_args, n_cores=n_cores, thread_func= cls._distribute_chunk_process_store_thread)
        
        # restore connection to db
        dt_inst.open_engine(open_conn=conn_was_open)
            
        return res
        
    @staticmethod
    def _distribute_chunk_process_store_thread(args):
        '''Passes elements and doctable instance to store in doctable.'''
        
        # thread for parsing chunks with distinct connection to database
        element_chunk, parse_func, dt_inst, static_args = args[0], args[1], args[2], args[3:]
        
        # open a connection in this process
        dt_inst.open_engine(open_conn=True)
        
        parsed = list()
        for el in element_chunk:
            parsed.append(parse_func(el, dt_inst, *static_args))
        return parsed
    
    
    @classmethod
    def _distribute_chunk_process(cls, elements, parse_func, *parse_static_args, n_cores=None, thread_func=None):
        '''Applies parse_func to elements distributed to processes in chunks.'''
        
        if thread_func is None:
            thread_func = cls._distribute_chunk_process_thread
        
        # decide on number of cores
        if n_cores is None:
            n_cores = min([os.cpu_count(), len(elements)])
        else:
            n_cores = min([os.cpu_count(), len(elements), n_cores])
        
        with Pool(processes=n_cores) as p:
            # break into chunks
            chunk_size = math.ceil(len(elements)/p._processes)
            chunks = [(elements[i*chunk_size:(i+1)*chunk_size], parse_func, *parse_static_args)
                        for i in range(p._processes)]
                      
            # map parse_func and then unchunk
            parsed = [el for parsed_chunk in p.map(thread_func, chunks) 
                      for el in parsed_chunk]
        return parsed
    
    @staticmethod
    def _distribute_chunk_process_thread(args):
        # thread for parsing distributed processes
        element_chunk, parse_func, static_args = args[0], args[1], args[2:]
        
        parsed = list()
        for el in element_chunk:
            parsed.append(parse_func(el, *static_args))
        return parsed
        


        
        
        