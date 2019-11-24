


class DocParser:
    '''Class that maintains convenient functions for parsing Spacy doc objects.'''

    # NOT CURRENTLY BEING USED
    #default_parsetree_tok_info = {
    #    'pos': lambda tok: tok.pos_, 
    #    'tag': lambda tok: tok.tag_, 
    #    'dep': lambda tok: tok.dep_, 
    #    'ent_type': lambda tok: tok.ent_type_ if tok.ent_type_ != '' else None,
    #}
    
    @classmethod
    def get_parsetree(cls, doc, parse_tok_func=None, parse_tok_args=dict(), parsetree_tok_info=dict(), tok_attrname='tok', children_attrname='children'):
        '''Extracts parsetree from spacy doc objects.
        Args:
            doc (spacy.Doc object): doc to generate parsetree from.
            parse_tok_func (function): used to parse token. If none, reverts to build-in token parser. Added so 
                users could create a custom function instead of using the built-in.
            parse_tok_args (dict): to be pased to .parse_tok(), which is applied to tok_attrname in parsing tree.
                This part is a little weird, but I had to include tok_attrname instead of rely on user passing
                it through parsetree_tok_info so that it could use the underlying token (parameter defaults).
            parsetree_tok_info (str->func): maps token attributes to attributes in resulting parse tree
            tok_attrname (str): attribute name for actual token ext, automatically included in parsetree result
            children_attrname (str): attribute name for list of children object in resulting parsetree
        '''
        
        if parse_tok_func is None:
            parse_tok_func = cls.parse_tok
        #if parsetree_tok_info is None:
        #    parsetree_tok_info = dict()#cls.default_parsetree_tok_info
        
        sent_trees = [
            cls._recurse_parsetree(sent.root, parsetree_tok_info, tok_attrname, children_attrname, parse_tok_func, parse_tok_args) 
            for sent in doc.sents
        ]
        return sent_trees
        
    @classmethod
    def _recurse_parsetree(cls, tok, parsetree_tok_info, tok_attrname, children_attrname, parse_tok_func, parse_tok_args):
        tok_info = {attr:info_func(tok) for attr, info_func in parsetree_tok_info.items()}
        node = {**tok_info, 'tok': parse_tok_func(tok, **parse_tok_args), children_attrname:list()}
        
        # add each child and their children
        for child in tok.children:
            child_node = cls._recurse_parsetree(child, parsetree_tok_info, tok_attrname, children_attrname, parse_tok_func, parse_tok_args)
            node[children_attrname].append(child_node)

        return node
        
    
    @classmethod
    def tokenize_doc(cls, doc, split_sents=False, merge_ents=False, merge_noun_chunks=False, ngrams=list(), spacy_ngram_matcher=None, ngram_sep=' ', use_tok_args=dict(), parse_tok_args=dict()):
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
    def parse_tok(tok, replace_num=None, replace_digit=None, lemmatize=False, normal_convert=None, format_ents=True, ent_convert=None):
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
        
        