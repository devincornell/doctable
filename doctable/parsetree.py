
from functools import reduce

class ParseTree:
    tree = None
    nodes = None
    root = None
    def __init__(self):
        # create from either from_tok or from_dict
        pass
    
    @staticmethod
    def from_tok(root_tok, *args, **kwargs):
        
        if '' in (root_tok.dep_, root_tok.tag_, root_tok.pos_):
            raise ValueError('Both the Spacy tagger and parser must '
                'be enabled to use a ParseTree.')
        
        # build tree object and keep reference of ordered tokens
        pt = ParseTree()
        pt.tree = ParseNode.from_tok(root_tok, *args, **kwargs)
        pt.make_node_list()
        return pt
    
    @staticmethod
    def from_dict(tdict):
        # build tree object and keep reference of ordered tokens
        pt = ParseTree()
        pt.tree = ParseNode.from_dict(tdict)
        pt.make_node_list()
        return pt
    
    def asdict(self):
        return self.tree.asdict()
    
    def make_node_list(self):
        self.nodes = self.tree.get_descendant_list()
        self.root = self.nodes[[n.dep for n in self.nodes].index('ROOT')]
        
    def __len__(self):
        return len(self.nodes)
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of tokens.'''
        return self.nodes[ind]
    
    def __iter__(self):
        return iter(self.nodes)
    


    def get_ents(self):
        if self[0].ent is None:
            raise ValueError('ParseTree needs to have "ent_type" property '
                'to use .get_ents().')
        return [n for n in self if n.ent!='']
    
    def get_subj_verb_obj(self):
        triplets = list()
        for node in self:
            if node.pos in ('VERB','ADV'):
                rel = (self.child_dep(node,'nsubj'), node, self.child_dep(node,'dobj'))
                triplets.append(rel)
        return triplets

    @staticmethod
    def child_dep(node, dep_type): # gets first child where node.dep==dep_type.
        for c in tok.children:
            if c.dep == dep_type:
                return c
        return None
    
    def print_ascii_tree(self):
        '''Print out an ascii tree.
        taken from: https://stackoverflow.com/questions/32151776/visualize-tree-in-bash-like-the-output-of-unix-tree
        '''
        self._print_ascii_tree(self.root, 0)
        
    @classmethod
    def _print_ascii_tree(cls, node, level, last=False, sup=[]):
        def update(left, i):
            if i < len(left):
                left[i] = '   '
            return left
        branch = '├'
        pipe = '|'
        end = '└'
        dash = '─'

        print(''.join(reduce(update, sup, ['{}  '.format(pipe)] * level)) \
              + (end if last else branch) + '{} '.format(dash) \
              + '({}) {}'.format(node.dep, node.tok))
        if len(node.childs) > 0:
            level += 1
            for node in node.childs[:-1]:
                cls._print_ascii_tree(node, level, sup=sup)
            if len(node.childs) > 1:
                cls._print_ascii_tree(node.childs[-1], level, True, [level] + sup)

        

class ParseNode:
    i = None
    tok = None
    pos = None
    dep = None
    tag = None
    info = None
    parent = None
    childs = None
    
    def __init__(self):
        pass
    
    @staticmethod
    def from_tok(tok, tok_parse_func, info_func_map=dict(), parent=None):
        pn = ParseNode()
        pn.i = tok.i
        pn.tok = tok_parse_func(tok)
        pn.pos = tok.pos_
        pn.dep = tok.dep_
        pn.tag = tok.tag_
        pn.info = {attr:func(tok) for attr,func in info_func_map.items()}
        
        # recursive constructor
        pn.parent = parent
        pn.childs = [ParseNode.from_tok(c, tok_parse_func, info_func_map=info_func_map, parent=pn) 
                       for c in tok.children]
        return pn
    
    @staticmethod
    def from_dict(ndict, parent=None):
        pn = ParseNode()
        pn.i = ndict['i']
        pn.tok = ndict['tok']
        pn.pos = ndict['pos']
        pn.dep = ndict['dep']
        pn.tag = ndict['tag']
        pn.info = ndict['info']
        pn.parent = parent
        pn.childs = [ParseNode.from_dict(c, parent=pn) for c in ndict['childs']]
        return pn
        
    def asdict(self):
        '''Convert self to a dict.'''
        node = dict(
            i=self.i,
            tok=self.tok,
            pos=self.pos,
            tag=self.tag,
            dep=self.dep,
            info=self.info,
            childs=[c.asdict() for c in self.childs],
        )
        return node
        
            
    def __str__(self):
        return 'ParseNode({})'.format(self.tok)
    
    def __repr__(self):
        return str(self)
    

    

        
        
    def get_descendant_list(self):
        '''Get list of self and descendants to generate sorted node list.'''
        nodes = [self]
        for child in self.childs:
            nodes += child.get_descendant_list()
        return list(sorted(nodes,key=lambda n:n.i))
    