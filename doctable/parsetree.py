
from functools import reduce

class ParseTree:
    def __init__(self, ptree_dict):
        
        # build tree object and keep reference of ordered tokens
        self.tree = ParseNode(ptree_dict)
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
        '''Get list of self and descendants to generate node list.'''
        nodes = [self]
        for child in self.childs:
            nodes += child.get_descendant_list()
        return list(sorted(nodes,key=lambda n:n.i))
    