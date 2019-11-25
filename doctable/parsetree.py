


class ParseTree:
    def __init__(self, ptree_dict):
        
        # build tree object and keep reference of ordered tokens
        self.tree = ParseNode(ptree_dict)
        self.node_l = self.tree.get_descendant_list()
        
    def __len__(self):
        return len(self.node_l)
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of tokens.'''
        return self.node_l[ind]
    
    def __iter__(self):
        return iter(self.node_l)

    def get_ents(self):
        return self.tree.get_descendant_ents()

class ParseNode:
    def __init__(self, ptree_dict):
        
        req_prop = ('i','tok','pos','dep','tag','childs',)
        if not all([k in ptree_dict for k in req_prop]):
            raise ValueError('A ParseTree should have at least the keys '
                '{}'.format(req_prop))
        
        self.i = ptree_dict['i']
        self.tok = ptree_dict['tok']
        self.pos = ptree_dict['pos']
        self.tag = ptree_dict['tag']
        self.dep = ptree_dict['dep']
        self.ent = ptree_dict.get('ent_type')
        
        # recursive constructor
        self.childs = [ParseNode(c) for c in ptree_dict['childs']]
        
        # keeping any non-standard properties
        self.info = {k:v for k,v in ptree_dict.items() if k not in req_prop}
        
        # set parent values
        if self.dep == 'ROOT':
            self.parent = None
        for child in self.childs:
            child.parent = self
    
    def __str__(self):
        return 'ParseNode({})'.format(self.tok)
    
    def __repr__(self):
        return str(self)
        
    def get_descendant_list(self):
        '''Get list of self and descendants.'''
        nodes = [self]
        for child in self.childs:
            nodes += child.get_descendant_list()
        return list(sorted(nodes,key=lambda n:n.i))
    
    def get_descendant_ents(self):
        if self.ent is None:
            raise ValueError('ParseTree needs to have "ent_type" property')
        
        ent_l = [t for t in self.get_descendant_list() if t.ent != '']
        if self.ent != '':
            ent_l.append(self)
        return  ent_l

    