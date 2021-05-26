import re
from multiprocessing import Pipe, Process
import math
import os
from doctable.util import Distribute
from doctable.parse import ParseTree


class DocParser:
    '''Class that maintains convenient functions for parsing Spacy doc objects.'''
    
    #CLOSE_SIGNAL = (math.pi + math.e)/3 # random number to indicate close
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
    
        
    ############################# Parsetree Extraction ###############################
    
    @classmethod
    def get_parsetrees(cls, doc, parse_tok_func=None, userdata_map=dict(), merge_ents=False, 
            spacy_ngram_matcher=None, merge_noun_chunks=False):
        '''Extracts parsetree from spacy doc objects.
        Args:
            doc (spacy.Doc object): doc to generate parsetree from.
            parse_tok_func (func): function used to convert token to 
                a string representation. Usually a lambda function 
                wrapping some variant of self.parse_tok().
            userdata_map (dict<str->func>): attribute to function 
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
        cls.apply_doc_transform(
            doc, 
            merge_ents=merge_ents, 
            spacy_ngram_matcher=spacy_ngram_matcher, 
            merge_noun_chunks=merge_noun_chunks
        )
        
        sent_trees = [
            ParseTree(sent.root, parse_tok_func, userdata_map=userdata_map)
            for sent in doc.sents
        ]
        return sent_trees
        
    ############################# Tokenizing ###############################
    
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
        cls.apply_doc_transform(doc, 
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
    def parse_tok(tok, num_replacement=None, digit_replacement=None, lemmatize=False, normal_convert=None, 
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
        
        # replace characters
        if digit_replacement is not None and tok.is_digit:
            return digit_replacement
        if num_replacement is not None and tok.like_num:
            return num_replacement
        
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
                return ' '.join([t.strip().lower() for t in tok.text.split()]).capitalize()
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
    def apply_doc_transform(doc, merge_ents=True, spacy_ngram_matcher=None, merge_noun_chunks=False):
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
        return doc # just in case user tries to assign
    
    @staticmethod
    def merge_ngrams(toks, ngrams, ngram_sep=' '):
        '''Merges manually specified consecutive tokens into single tokens.
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
    

        
    @classmethod
    def parse_text_chunks(cls, text, nlp, parse_funcs={}, doc_transform=None,
                             chunk_sents=1000, split_re='([\?\!\.]+)(?=[\WA-Z])'):
        '''Parse text in paragraph by sentences.
        Args:
            text (str): (preprocessed) text document to parse
            nlp (spaCy parser): with .pipe() method to parse documents
            parse_funcs (list<func>): convert doc to 
            chunk_sents (int): number of sentences used in each chunk to 
                be parsed. Max size for single spacy doc is 1 million 
                chars. If av num chars per sent is 75-100, a size of
                3000 means each chunk will have approx 300k characters.
                Hopefully, on average small enough. Larger value means
                more memory but faster processing.
        '''
        if doc_transform is None:
            doc_transform = lambda x: x
        
        # split into paragraphs and chunks
        text_chunks = cls._split_texts(text, chunk_sents, split_re)
        
        # flatten texts into single list and record paragraph,chunk ids
        parids = [(i,ch) for i, par in enumerate(text_chunks) for ch in par]
        parids, allchunks = list(zip(*parids))
                
        # parse each document, store in structure
        last_idx = 0 # i is paragraph, j is chunk
        parsed_par_chunks = [[]] # list of par->chunks
        for idx, doc in zip(parids, nlp.pipe(allchunks)):
            doc = doc_transform(doc)
            parsed = {k:v(doc) for k,v in parse_funcs.items()}
            #print(idx)
            if idx != last_idx:
                parsed_par_chunks.append([])
                #print('adding el', idx)
            parsed_par_chunks[-1].append(parsed)
            last_idx = idx
            del doc
        
        return parsed_par_chunks
    
    @staticmethod
    def _split_texts(text, chunk_sents, split_re):
        sents = [s for s in re.split(split_re, text) if len(s.split())>0]
        n_chunks = math.ceil(len(sents)/(2*chunk_sents))
        textblocks = [''.join(sents[i*chunk_sents*2:(i+1)*chunk_sents*2]) 
                        for i in range(n_chunks)]
        return textblocks
        
        
    #################### DISTRIBUTED PARSING METHODS #######################
    @classmethod
    def distribute_parse(cls, texts, spacynlp, parsefunc=None, preprocessfunc=None, 
        dt_inst=None, paragraph_sep=None, workers=None):
        '''Distributes text parsing across multiple processes in chunks.
        Args:
            texts (list): list of raw texts to process
            spacynlp (spacy nlp object): for applying .pipe() to doc chunks
            parsefunc (func): convert spacy doc object to storage represenation
                By defaut uses DocParser.tokenize_doc().
            preprocessfunc (func): process text before parsing. Uses 
                DocParser.preprocess() by default.
            dt_inst (doctable instance): if included, will pass to parsefunc as
                second argument. Usually to do this, you'll create a function
                which calls some overloaded version of .tokenize_doc() and then
                calls dt_inst.insert() to place in database.
            paragraph_sep (str or None): if defined, will distribute parsing across
                paragraphs and leave paragraph structure of docs in nested lists.
            workers (int): number of processes to create.
        Returns:
            output of parsing
        '''
        
        if dt_inst is not None and parsefunc is None:
            raise ValueError('When dt_inst is provided, parsefunc must be provided '
                'to insert elements into database after parsing.')
        
        # default parse functions
        if preprocessfunc is None:
            preprocessfunc = cls.preprocess
        if parsefunc is None:
            parsefunc = cls.tokenize_doc
        
        
        # split into paragraphs
        if paragraph_sep is not None:
            texts, ind = list(zip(*[(par.strip(),i) for i,text in enumerate(texts) 
                            for par in text.split(paragraph_sep)]))
        
        # perform actual parsing
        thread_args = (spacynlp, parsefunc, preprocessfunc, dt_inst)
        #parsed = cls.distribute_chunks(cls._distribute_parse_thread, texts, 
        #                               *thread_args, workers=workers)
        with Distribute(workers) as d:
            parsed = d.map_insert(cls._distribute_parse_thread, texts,
                                 *thread_args, dt_inst=dt_inst)
            
        # fold paragraphs back into document list
        if paragraph_sep is not None:
            parsed_docs = list()
            last_i, last_ind = 0, 0
            for i in range(len(ind)):
                if ind[i] != last_ind:
                    parsed_docs.append(parsed[last_i:i])
                    last_ind = ind[i]
                    last_i = i
                elif i == len(ind)-1:
                    parsed_docs.append(parsed[last_i:])
            parsed = parsed_docs
        
        return parsed
    
    #@staticmethod
    #def _distribute_parse_thread(text, nlp, parsefunc, preprocessfunc, dt_inst):
    #    parsed = parsefunc(nlp(preprocessfunc(text)))
        
            
    @staticmethod
    def _distribute_parse_thread(texts_chunk, nlp, parsefunc, preprocessfunc, dt_inst):
        
        addtnl_args = list()
        if dt_inst is not None:
            dt_inst.open_engine(open_conn=True)
            addtnl_args.insert(0,dt_inst)
        
        parsed_docs = list()
        for doc in nlp.pipe(map(preprocessfunc, texts_chunk)):
            parsed_docs.append(parsefunc(doc, *addtnl_args))
            
        if dt_inst is not None:
            dt_inst.close_engine()
            
        return parsed_docs
    
    @staticmethod
    def spacy_parse_chunks(text, nlp, parsefuncs=list(), chunk_size=10):
        '''Parses document in sentence chunks to reduce memory use.
        '''
        # sentence is smallest unit spacy analyzes
        # multiply by two since split includes punctuation too
        sents = re.split('[\?\!\.]', text)
        n_chunks = math.ciel(len(sents)/(chunk_size*2))
        sent_chunks = [sents[i*chunk_size*2:(i+1)*chunk_size*2] 
                           for i in range(n_chunks)]
        for sent_chunk in sent_chunks:
            subdoc = nlp(''.join(sent_chunk))