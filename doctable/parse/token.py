from __future__ import annotations
import typing
import dataclasses
import collections

#from doctable.parse.parsetree import ParseTree

class PropertyNotAvailable(Exception):
    template = '{prop} is not available in Token because {parsefeatname} was not enabled while processing with Spacy.'
    def __init__(self, prop, parsefeatname):
        message = self.template.format(prop=prop, parsefeatname=parsefeatname)
        super().__init__(message)


@dataclasses.dataclass(repr=True)
class Token:
    ''' Object representing a single token.
    Attrs:
        i: index of token in original sentence
        text: text representation of token
        dep: dependency relation estimated in spacy
        tag: dependency tag estimated by spacy
        childs: list of children Tokens
        tree: reference to associated parsetree
        otherdata: containes 'pos' and 'ent' data from spacy
        userdata: data provided by user (usually generated 
            from userdata_map in from_spacy()).
        parent: reference to parent Token (populated in 
            __post_init__).
    '''
    i: int
    text: str
    dep: str
    tag: str
    childs: list
    otherdata: dict = dataclasses.field(default_factory=dict)
    userdata: dict = dataclasses.field(default_factory=dict)
    
    # assigned by parsetree
    tree: typing.Any = dataclasses.field(default=None, repr=False)
    parent: typing.Any = dataclasses.field(default=None, repr=False)

    def __post_init__(self):
        ''' Create references to parents recursively.
        '''
        # adding references to parent
        for child in self.childs:
            child.parent = self

        # set up for easy subscripting
        self.chainmap = collections.ChainMap(self.__dict__, 
                            self.otherdata, self.userdata)
    
    ########################## Factory methods ##########################
    @classmethod
    def from_spacy(cls, spacy_tok: typing.Any, 
                        text_parse_func:typing.Callable=lambda t: t.text, 
                        userdata_map: dict={}, 
                        parent: Token = None, 
                        tree:typing.Any=None) -> Token:
        ''' Return tokens recursively from spacy_tok object.
        Args:
            spacy_tok: token to extract userdata from
            text_parse_func: mapping to store text data
            userdata_map: used to create custom user data
            tree (doctable.parse.ParseTree): reference to associated ParseTree
        '''
        newtoken = cls(
            i = spacy_tok.i,
            dep = spacy_tok.dep_,
            tag = spacy_tok.tag_,
            text = text_parse_func(spacy_tok),
            otherdata = {
                'pos': spacy_tok.pos_ if spacy_tok.doc.is_tagged else None,
                'ent': spacy_tok.ent_type_ if spacy_tok.doc.is_nered else None,
            },
            userdata = {attr:func(spacy_tok) for attr,func in userdata_map.items()},
            
            # references
            tree = tree,
            childs = [cls.from_spacy(child, text_parse_func=text_parse_func, 
                        userdata_map=userdata_map, tree=tree) 
                        for child in spacy_tok.children],
        )
        return newtoken

    @classmethod
    def from_dict(cls, tok_data: dict, tree: typing.Any=None):
        ''' Create new token recursively using a dictionary tree structure.
        Args:
            tok_data: dictionary containing current token information
            tree (ParseTree): reference to associated parsetree
        '''
        newtoken = cls(
            i = tok_data['i'],
            text = tok_data['text'],
            dep = tok_data['dep'],
            tag = tok_data['tag'],
            otherdata = tok_data['otherdata'],
            userdata = tok_data['userdata'],
            childs = [cls.from_dict(td) for td in tok_data['childs']],
        )
        return newtoken

    def set_tree(self, tree):
        self.tree = tree

    ########################## Serialization ##########################
    def as_dict(self):
        ''' Convert self to a dict tree - used when storing data.
        '''
        data = dict(
            i=self.i,
            text=self.text,
            tag=self.tag,
            dep=self.dep,
            otherdata=self.otherdata,
            userdata=self.userdata,
            childs=[c.as_dict() for c in self.childs],
        )
        return data
        
    ########################## Built-In Methods ##########################
    def __str__(self):
        return self.text
    
    #def __repr__(self):
    #    return "{name}(i={i}, text={text}, dep={dep}, \
    #        tag={tag}, otherdata={otherdata}, userdata={userdata}, \
    #        childs={childs})".format(**dict(
#                name=self.__class__.__name__,
    #            i=self.i,
    #            text=self.text,
    #            dep = self.dep,
    #        )
    
    def __getitem__(self,ind):
        ''' Access token attrs or user-provided data.
        '''
        return self.chainmap[ind]
    
    def __iter__(self):
        ''' Iterate over children.
        '''
        return iter(self.childs)

    ########################## Properties ##########################
    @property
    def is_root(self):
        ''' Check if token is root or not.'''
        return self.parent is None

    @property
    def pos(self):
        ''' Access pos data.
        Raises:
            PropertyNotAvailable: pos was not included in original spacy object.
        '''
        if self.otherdata['pos'] is None:
            raise PropertyNotAvailable('Part-of-speech tag', 'POS-tagging')
        return self.otherdata['pos']

    @property
    def ent(self):
        ''' Access ent data.
        Raises:
            PropertyNotAvailable: ent was not included in original spacy object.
        '''
        if self.otherdata['ent'] is None:
            raise PropertyNotAvailable('Entity type', 'NER')
        return self.otherdata['ent']

    ########################## ParseTree Navigation Functions ##########################

    def get_childs(self, dep: str=None, pos: str=None, matchfunc:typing.Callable=None):
        ''' Get children with the specified relations.
        Args:
            dep (sequence or string): dependency relations to match on.
            pos (sequence or string): pos to match on.
            matchfunc (function or None): additional custom matching function.
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

    def get_child(self, *args, allow_multiple: bool=False, **kwargs):
        ''' Get first child with the given dependency relation.
        Args:
            *args: passed to get_childs
            allow_multiple: don't allow 
            **kwargs: passed to get_childs
        Raises:
            ValueError when the token has more than one dependency with the 
                given relation.
        '''
        childs = self.get_childs(*args, **kwargs)
        if len(childs) == 1 or (len(childs) and allow_multiple):
            return childs[0]
        elif not len(childs):
            return None
        else:
            raise ValueError(f'There is more than one dependency matching {args}, {kwargs}.')
    
    def get_preps(self, as_str:bool=False):
        ''' Gets chained prepositional phrases starting at the current token.
        Returns:
            tuple of prep, pobj.
        '''
        preps = list()
        for prep in self.get_childs({'prep', 'dative'}):
            if as_str:
                pairs = (prep.t, [p.t for p in prep.get_childs('pobj') if p is not None])
            else:
                pairs = (prep, [p for p in prep.get_childs('pobj') if p is not None])
            preps.append(pairs)
        
        return preps
    
    def bubble_accum(self, func: typing.Callable):
        ''' Bubble up results into a list.
        Args:
            func: function that accepts a Token and returns a list
                of results that will be concatenated at each level
                of the tree.
        Example:
            `self.bubble_accum(lambda n: [n])` would return a list
                of (unordered) tokens in the tree below the given 
                node.
        '''
        aggregated_list = func(self)
        for child in self.childs:
            aggregated_list += child.bubble_accum(func)
        return aggregated_list



