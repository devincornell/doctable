
from functools import reduce

class ParseTree:
    root = None
    def __init__(self, root_node, *args, **kwargs):
        '''Create from dict parsetree or spacy sentence root.'''
        
        # check that spacy token is good
        if not isinstance(root_node, dict): # root node is spacy token
            if not root_node.doc.is_parsed:
                raise ValueError('Both the Spacy tagger and parser must '
                    'be enabled to make a ParseTree.')
        
        # root is reference to entire tree
        self.root = Token(root_node, *args, tree=self, **kwargs)
        _tokens = self.bubble_accum(lambda n: [n])
        self._tokens = list(sorted(_tokens,key=lambda n:n.i))
        
    @property
    def toks(self):
        ''' List of token texts.
        '''
        return [n.text for n in self._tokens]
        
    def __str__(self):
        return 'ParseTree({})'.format(self.toks)
    
    def __repr__(self):
        return str(self)
        
    def __len__(self):
        return len(self._tokens)
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of _tokens.'''
        return self._tokens[ind]
    
    def __iter__(self):
        return iter(self._tokens)
    
    def to_dict(self):
        return self.root.to_dict()
    
    def bubble_accum(self, func):
        '''Applies func to each node and bubbles up accumulated result (like reduce).
        Args:
            func (function): apply function to an object returning list.
        '''
        return self.root.bubble_accum(func)
    
    def bubble_reduce(self, func, init_data):
        '''Applies func to each node and bubbles up accumulated list of results.
        Args:
            func (function): apply function to an object returning list.
            init_data (any type): initial data to pass through reduce function
        '''
        return self.root.bubble_reduce(func, init_data)
    
    
    def display(self, pad=15, base=10, **kwargs):
        ''' Print out an ascii tree.
        '''
        self.print_tree_recursive(self.root, pad, base, **kwargs)
        
    @classmethod
    def print_tree_recursive(cls, tok, pad, base, level=0, root_str='{text}', dep_str=' -{dep}> {text}'):
        if level == 0:
            print(root_str.format(**tok.to_dict()).ljust(pad-(pad-base)), end='')
        else:
            print(dep_str.format(**tok.to_dict()).ljust(pad), end='')

        if len(tok.childs)==0: # base case
            print('\n' + ' '*(level*pad-(pad-base)), end='')
        else:
            for child in tok.childs:
                cls.print_tree_recursive(child, pad, base, level+1, root_str, dep_str)


class Token:
    parent = None
    childs = []
    i = None
    text = None
    dep = None
    tag = None
    info = None
    tree = None
    
    def __init__(self, node, text_parse_func=None, info_func_map=dict(), parent=None, tree=None):
        '''Construct from either a dictionary or spacy token.
        Args:
            if node is spacy.Token:
                node (spacy.Token): token to extract info from
                text_parse_func (dict<str:func>): mapping to store text
                info_func_map (dict<str:func>): data that will go into .info
            if node is dict:
                node (dict<str:any>): dictionary of node properties
                parent (spacy.Token): parent of current node
                text_parse_func: unused
                info_func_map: unused
        '''
        self.parent = parent
        self.tree = tree
        
        if not isinstance(node, dict): # node is spacy token
            tok = node
            self.i = tok.i
            self.text = text_parse_func(tok) if text_parse_func is not None else tok.text
            self.dep = tok.dep_
            self.tag = tok.tag_
            self.info = {attr:func(tok) for attr,func in info_func_map.items()}
            
            self.childs = [self.__class__(child, text_parse_func=text_parse_func, \
                            info_func_map=info_func_map, parent=self, tree=tree) 
                           for child in tok.children]
            
            self._pos = tok.pos_ if tok.doc.is_tagged else None
            self._ent = tok.ent_type_ if tok.doc.is_nered else None    

        else: # node is a dictionary (probably re-creating token from stored dictionary)
            ndict = node
            self.i = ndict['i']
            self.text = ndict['text']
            self.dep = ndict['dep']
            self.tag = ndict['tag']
            self.info = ndict['info']
            self.childs = [self.__class__(c, parent=self) for c in ndict['childs']]
            self._pos = ndict['pos']
            self._ent = ndict['ent']

    def to_dict(self):
        '''Convert self to a dict - used when storing data.
        '''
        node = dict(
            i=self.i,
            text=self.text,
            tag=self.tag,
            dep=self.dep,
            info=self.info,
            childs=[c.to_dict() for c in self.childs],
            pos=self._pos,
            ent=self._ent,
        )
        return node
        
    ########################## Built-In Methods ##########################
    def __str__(self):
        return f'{self.__class__.__name__}({self.text})'
    
    def __repr__(self):
        return str(self)
    
    def __getitem__(self,ind):
        return self.info[ind]
    
    def __iter__(self):
        return iter(self.childs)

    ########################## Properties ##########################
    @property
    def t(self):
        return self.text

    @property
    def pos(self):
        if self._pos is None:
            raise AttributeError('Part-of-speech tag is not available in Token because '
                'POS-tagging was not enabled while processing with Spacy.')
        return self._pos

    @property
    def ent(self):
        if self._ent is None:
            raise AttributeError('Entity tag is not available in Token because '
                'NER was not enabled while processing with Spacy.')
        return self._ent

    @property
    def is_none(self):
        return False

    ########################## Navigation Functions ##########################

    def get_childs(self, dep=None, pos=None, matchfunc=None):
        ''' Get children with the given dependency relation.
        Args:
            dep (sequence or string): dependency relations to match on.
            pos (sequence or string): pos to match on.
            matchfunc (function or None): custom matching function.
        '''
        if isinstance(dep, str):
            dep = set([dep])

        if isinstance(pos, str):
            pos = set([pos])

        childs = list()
        for c in self.childs:
            if (dep is None or c.dep in dep): # nested to make more readable?
                if (pos is None or c.pos in pos):
                    if (matchfunc is None or matchfunc(c)):
                        childs.append(c)
        return childs

    def get_child(self, *args, first=False, **kwargs):
        ''' Get first child with the given dependency relation.
        Args:
            deprel (sequence or string): dependency relations to match on.
        Raises:
            ValueError when the token has more than one dependency with the 
                given relation.
        '''
        childs = self.get_childs(*args, **kwargs)
        if len(childs) == 1 or (len(childs) and first):
            return childs[0]
        elif not len(childs):
            return NoneToken()
        else:
            raise ValueError(f'There is more than one dependency matching {args}, {kwargs}.')
    
    def get_preps(self, as_str=False):
        ''' Gets chained prepositional phrases starting at the current token.
        Returns:
            tuple of prep, pobj.
        '''
        #if preps is None:
        preps = list()
        for prep in self.get_childs({'prep', 'dative'}):
            if as_str:
                pairs = (prep.t, [p.t for p in prep.get_childs('pobj') if not p.is_none])
            else:
                pairs = (prep, [p for p in prep.get_childs('pobj') if not p.is_none])
            preps.append(pairs)
                
        return preps
    
    ########################## Accumulation Functions ##########################
    def bubble_accum(self, func):
        aggregated_list = func(self)
        for child in self.childs:
            aggregated_list += child.bubble_accum(func)
        return aggregated_list
    
    def bubble_reduce(self, func, agg_data):
        agg_data = func(self, agg_data)
        for child in self.childs:
            agg_data = child.bubble_reduce(func, agg_data)
        return agg_data
    
class NoneToken(Token):
    def __init__(self):
        pass
    @property
    def is_none(self):
        return True
    def __str__(self):
        return 'NoneToken'