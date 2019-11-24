

def DocParser:
    '''Class that maintains convenient functions for parsing Spacy doc objects.'''
    def parse_tok(tok, capitalize_ents=True, replace_num='__NUM__', replace_digit='__DIGIT__', entity_map=dict()):
        '''Convert spacy token object to string.
        Args:
            tok (spacy token or span): token object to convert to string.
            capitalize_ents (bool): Replace whitespace with space and capitalize ents.
            replace_num (bool): Replace number following tok.like_num (includes "five", 
                or 5) with a special token (i.e. __NUM__). None means no replacement.
            replace_digit (bool): Replace digit meeting tok.is_digit with special token. 
                Only used when replace_num is None.
                
            entity_map (dict): map from ent_type->function where will use
                special conversion function to convert specific entity types.
        '''
        
        number_ents = ('NUMBER','MONEY','PERCENT','QUANTITY','CARDINAL','ORDINAL')
        
        if tok.ent_type_ == '': # non-entity token
            return tok.text.lower()
        
        else: # token is entity
        elif tok.ent_type_ in number_ents:
            return tok.ent_type_
        else:
            return tok.text

    def use_tok(tok, no_whitespace=True, no_punct=False, no_num=False, no_digit=True, no_stop=False):
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
            
        return do_use_tok

    def parse_doc(doc, split_sents=True, merge_ents=False, use_tok_args=dict()):
        '''Parse spacy doc object.
        Args:
            split_sents (bool): parse into list of sentence tokens using doc.sents.
            merge_ents (bool): merge multi_word entities into same
            
        '''
            
        if merge_ents:
            for ent in doc.ents:
                ent.merge(tag=ent.root.tag_, ent_type=ent.root.ent_type_)
                
        if split_sents:
            return [[self.parse_tok(tok) for tok in sent] for sent in doc.sents]
        else:
            return [self.parse_tok(tok) for tok in doc if use_tok(tok)]