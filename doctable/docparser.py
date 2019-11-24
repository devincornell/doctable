

class DocParser:
    '''Class that maintains convenient functions for parsing Spacy doc objects.'''
    
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
                return other_convert(tok)
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
    def use_tok(tok, no_whitespace=True, no_punct=False, no_num=False, no_digit=False, no_stop=False, no_ent=False):
        '''Decide to use token or not (can be overridden).
        Args:
            no_whitespace (bool): exclude whitespace.
            no_punct (bool): exclude punctuation.
            no_num (bool): exclude numbers using tok.is_num.
            no_digit (bool): exclude digits using tok.is_digit.
            no_stop (bool): exclude stopwords.
        '''
        do_use_tok = True
        if no_whitespace:
            do_use_tok = do_use_tok and (tok.is_ascii and \
                not tok.is_space and len(tok.text.strip()) > 0)
        if no_punct:
            do_use_tok = do_use_tok and not tok.is_punct
            
        if no_stop:
            do_use_tok = do_use_tok and not tok.is_stop
            
        if no_whitespace:
            do_use_tok = do_use_tok and not tok.is_space
            
        if no_num:
            do_use_tok = do_use_tok and not tok.is_digit
            
        if no_digit:
            do_use_tok = do_use_tok and not tok.like_num
        
        if no_ent:
            do_use_tok = do_use_tok and tok.ent_type_ != ''
            
        return do_use_tok
    
    @classmethod
    def tokenize_doc(cls,doc, split_sents=False, merge_ents=False, matcher=None, use_tok_args=dict(), parse_tok_args=dict()):
        '''Parse spacy doc object.
        Args:
            split_sents (bool): parse into list of sentence tokens using doc.sents.
            merge_ents (bool): merge multi_word entities into same
            matcher (spacy Matcher): matcher object to use on the spacy doc.
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
        if matcher is not None:
            with doc.retokenize() as retokenizer:
                # merge custom matches
                if matcher is not None:
                    for match_id, start, end in matcher(doc):
                        retokenizer.merge(doc[start:end])
        if merge_ents:
            with doc.retokenize() as retokenizer:
                # merge entities
                for ent in doc.ents:
                    retokenizer.merge(ent)
                
        if split_sents:
            sents = [
                [cls.parse_tok(tok, **parse_tok_args) 
                 for tok in sent if cls.use_tok(tok, **use_tok_args)] 
                for sent in doc.sents
            ]
            return sents
        else:
            return [cls.parse_tok(tok, **parse_tok_args) 
                    for tok in doc if cls.use_tok(tok, **use_tok_args)]