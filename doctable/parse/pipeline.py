
from doctable.util.distribute import Distribute
from .parsefuncs import (
    preprocess, 
    tokenize, 
    parse_tok, 
    keep_tok, 
    merge_tok_spans, 
    merge_tok_ngrams, 
    get_parsetrees
)
import functools

components = {
    'preprocess': preprocess,
    'tokenize': tokenize,
    'parse_tok': parse_tok,
    'keep_tok': keep_tok,
    'merge_tok_spans': merge_tok_spans,
    'merge_tok_ngrams': merge_tok_ngrams,
    'get_parsetrees': get_parsetrees,
}


def Comp(func, *args, **kwargs):
    ''' Returns a pipeline component as a function with one positional arg.
        See components in this file to see available mappings.
    Args:
        *args: passed directly to component function
        **kwargs: passed directly to component function
    '''
    if isinstance(func, str):
        return functools.partial(components[func], *args, **kwargs)
    else:
        return functools.partial(func, *args, **kwargs)

def MultiComp(**funcs):
    ''' Add a component that returns a dictionary, each with separate parsers.
    Args:
        funcs (dict<str:func>): mapping from string to dictionary
    '''
    return functools.partial(funcwrap, **funcs)

def funcwrap(x, **funcs):
    ''' Used in MultiComp.'''
    return {name:func(x) for name, func in funcs.items()}

class ParsePipeline:
    ''' Class for creating pipelines for parsing text documents (or other elements).
    Primarily
    
    '''
    def __init__(self, components):
        ''' 
        Args:
            components (list<func>): list of components/functions to apply to the 
                input sequentially. See the component function in this script to 
                generate components.
        '''
        self.components = components
    
    def parse(self, doctext):
        ''' Parses document by applying each component function to doctext in turn.
        Args:
            doctext (str): text to be parsed. This can actually be anything to put into
                a pipeline.
        Returns:
            single parsed document object, output of last pipeline function
        '''
        doc = doctext
        for comp in self.components:
            doc = comp(doc)
        return doc
    
    def parsemany(self, doctexts, workers=1, override_maxcores=False):
        ''' Parse multiple documents distributed across workers.
        Args:
            doctexts (list<str>): elements to be parsed
            workers (int): number of processes to use
            override_maxcores (bool): in cases where processes may have
                low CPU utilization, you may want to create more processes
                than your computer has cores.
        Returns:
            list of parsed elements
        '''
        with Distribute(workers, override_maxcores=override_maxcores) as d:
            parsed = d.map_chunk(self.parsemany_thread, doctexts, self)
        return parsed
        
    @staticmethod
    def parsemany_thread(doctexts, parser):
        ''' Helper for .parsemany(). 
        '''
        parsed = list()
        for doctext in doctexts:
            parsed.append(parser.parse(doctext))
        return parsed
            
    
    


