


class ParseTree:
    def __init__(self, ptree_dict):
        
        # check to make sure they have the right information

        
        # build tree object and keep reference of ordered tokens
        self.tree = ParseNode(ptree_dict)
        self.ordered = self.tree.get_as_list()
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of tokens.'''
        return self.ordered[ind]
        

    def get_ents(self, ptree=None):
        if ptree is None:
            ptree = self.ptree
        
        ents = list()
        if ptree['ent_type'] is not None:
            ents.append((ptree['tok'], ptree['ent_type']))

        for child in ptree['children']:
            ents += self.get_ents(child)
        return ents

class ParseNode:
    def __init__(self, ptree_dict, is_root=True):
        
        req_tags = ('i','tok','pos','dep','tag','childs',)
        if not all([k in ptree_dict for k in req_prop]):
            raise ValueError('A ParseTree should have at least the keys '
                '{}'.format(req_prop))
        
        self.i = ptree_dict['i']
        self.tok = ptree_dict['tok']
        self.pos = ptree_dict['pos']
        self.tag = ptree_dict['tag']
        self.dep = ptree_dict['dep']
        
        # recursive constructor
        self.childs = [ParseNode(c, is_root=False) for c in ptree_dict['childs']]
        
        # keeping any non-standard properties
        self.info = ptree_dict
        for k in req_tags:
            del self.info[k]
        
        # set parent values
        if is_first:
            self.parent = None
        for child in self.childs:
            child.parent = self
    
    def __str__(self):
        return 'ParseNode({})'.format(self.tok)
    
    def get_as_list(self):
        # returns list including self and descendants
        nodes = [self]
        for child in self.childs:
            nodes += child.get_as_list()
        return list(sorted(nodes,key=lambda n:n.i))
