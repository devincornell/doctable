
from functools import reduce

class ParseTree:
    tree = None
    nodes = None
    root = None
    def __init__(self, root_node, *args, **kwargs):
        '''Create from dict parsetree or spacy sentence root.'''
        
        # check that spacy token is good
        if not isinstance(root_node, dict):
            if '' in (root_node.dep_, root_node.tag_, root_node.pos_):
                raise ValueError('Both the Spacy tagger and parser must '
                    'be enabled to use a ParseTree.')
        
        # root is reference to entire tree
        self.root = ParseNode(root_node, *args, **kwargs)
        nodes = self.bubble_accum(lambda n: [n])
        self.nodes = list(sorted(nodes,key=lambda n:n.i))
        
    def __str__(self):
        return 'ParseTree({})'.format(len(self.nodes))
    def __repr__(self):
        return str(self)
        
    def __len__(self):
        return len(self.nodes)
    
    def __getitem__(self,ind):
        '''Returns ith item in ordered list of tokens.'''
        return self.nodes[ind]
    
    def __iter__(self):
        return iter(self.nodes)
    
    def asdict(self):
        return self.root.asdict()
    
    def bubble_accum(self, func):
        return self.root.bubble_accum(func)
    
    def bubble_agg(self, func, init_data):
        return self.root.bubble_agg(func, init_data)
    
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
    
    def __init__(self, node, tok_parse_func=None, info_func_map=dict(), parent=None):
        '''Construct from either a dictionary or spacy token.'''
        self.parent = parent
        
        if isinstance(node, dict):
            ndict = node
            self.i = ndict['i']
            self.tok = ndict['tok']
            self.pos = ndict['pos']
            self.dep = ndict['dep']
            self.tag = ndict['tag']
            self.info = ndict['info']
            self.childs = [ParseNode(c, parent=self) for c in ndict['childs']]

            
        else: # node is spacy token
            tok = node
            self.i = tok.i
            self.tok = tok_parse_func(tok) if tok_parse_func is not None else tok.lower_
            self.pos = tok.pos_
            self.dep = tok.dep_
            self.tag = tok.tag_
            self.info = {attr:func(tok) for attr,func in info_func_map.items()}
            self.childs = [ParseNode(child, tok_parse_func=tok_parse_func, \
                            info_func_map=info_func_map, parent=self) 
                           for child in tok.children]
    
        
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
    
    def __getitem__(self,ind):
        return self.childs[ind]
    
    def __iter__(self):
        return iter(self.childs)
    
    def bubble_accum(self, func):
        '''Applies func to each node and bubbles up accumulated list of results.
        Args:
            func (function): apply function to an object returning list.
        '''
        aggregated_list = func(self)
        for child in self.childs:
            aggregated_list += child.bubble_accum(func)
        return aggregated_list
    
    def bubble_agg(self, func, agg_data):
        '''Applies func to each node and bubbles up accumulated results.
        Args:
            func (function): apply function to an object returning list.
        '''
        agg_data = func(self, agg_data)
        for child in self.childs:
            agg_data = child.bubble_agg(func, agg_data)
        return agg_data
    
    