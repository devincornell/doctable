
from glob import glob
import os
import zipfile
import re
from tqdm import tqdm
import spacy
from gutendocsdb import GutenDocsDB

from gutenberg.acquire.metadata import SleepycatMetadataCache
#from gutenberg.acquire.metadata import SqliteMetadataCache
from gutenberg.acquire import set_metadata_cache
from gutenberg.query import get_etexts
from gutenberg.query import get_metadata
from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers
from gutenberg.query import list_supported_metadatas
import gutenberg


import sys
sys.path.append('...')
import doctable

class GutenParser(doctable.DocParser):
    ''''''
    
    def __init__(self, dbfname, **kwargs):
        self.nlp = spacy.load('en')
        
        self.dbfname = dbfname
        self.db = GutenDocsDB(fname=self.dbfname)
        prev_ids = self.db.select('gutenid')
        
        # for whatever reason I think this is currently the last book
        self.ids = [i for i in range(61041) if i not in prev_ids]
        
        
    def parse_gutenberg(self, workers=None, verbose=False):
        '''Parse and store nss docs into a doctable.
        Args:
            years (list): years to request from the nss corpus
            dbfname (str): fname for DocTable to initialize in each process.
            workers (int or None): number of processes to create for parsing.
        '''
        
        self.db.clean_col_files('text')
        self.db.clean_col_files('par_toks')
        self.db.clean_col_files('par_ptrees')
        
        with doctable.Distribute(workers) as d:
            res = d.map_chunk(self.parse_guten_chunk, self.ids, self.nlp, 
                               self.dbfname, verbose)
        return res
    
    @classmethod
    def parse_guten_chunk(cls, ids, nlp, dbfname, verbose):
        '''Runs in separate process for each chunk of nss docs.
        Description: parse each fname and store into database
        Args:
            fnames (list<str>): list of filenames to read
            nlp (spacy parser): parser
            dbfname (str): filename of database to write into
            verbose (bool): print progress
        '''
        
        # create a new database connection
        db = GutenDocsDB(fname=dbfname)
        
        # set up gutenberg cache
        cache = SleepycatMetadataCache('guten_cache.sqlite')
        set_metadata_cache(cache)
        
        
        # define parsing functions and regex
        re_start = re.compile('\n\*\*\*.*START OF .* GUTENBERG .*\n')
        use_tok = lambda tok: cls.use_tok(tok, filter_whitespace=True)
        parse_tok = lambda tok: cls.parse_tok(tok, replace_num=True, format_ents=True)
        tokenize = lambda doc: cls.tokenize_doc(doc, merge_ents=True, 
                split_sents=True, parse_tok_func=parse_tok, use_tok_func=use_tok)
        parsetrees = lambda doc: cls.get_parsetrees(doc, merge_ents=True, parse_tok_func=parse_tok)
        
        # use loading bar or not
        if verbose:
            n = len(ids)
            iter = tqdm(enumerate(ids), total=n, ncols=50)
        else:
            iter = enumerate(ids)
        
        # loop through each potential document
        for i, idx in iter:
            #print('\n--> holding for lang ({})'.format(ids[0]))
            language = get_metadata('language', idx)
            #print('\n--> got lang:', language, '({})'.format(ids[0]))
            if 'en' in language:
                valid_etext = True
                try:
                    text = strip_headers(load_etext(i)).strip().replace('\r','')
                except gutenberg._domain_model.exceptions.InvalidEtextIdException:
                    valid_etext = False
                except gutenberg._domain_model.exceptions.UnknownDownloadUriException:
                    valid_etext = False
                except EOFError:
                    valid_etext = False # messed up unzipping text file?

                if valid_etext:
                    title = '\n'.join(get_metadata('title', idx))
                    author = '\n'.join(get_metadata('author', idx))
                    subject = '\n'.join(get_metadata('subject', idx))
                    language = '\n'.join(get_metadata('language', idx))
                    rights = '\n'.join(get_metadata('rights', idx))
                    formaturi = '\n'.join(get_metadata('formaturi', idx))

                    text_pars = [par.strip() for par in text.split('\n\n') 
                                    if len(par.strip()) > 0]

                    # parse by paragraph
                    par_toks, par_ptrees = list(), list()
                    for text_par in text_pars:
                        
                        # split into blocks so nothing too big for spacy
                        tsplit = text_par.split('.')
                        chunk_size = 10 # sentences
                        N = math.ciel(len(tsplit)/chunk_size)
                        textblocks = ['.'.join(ts[i*N:(i+1)*N])+'.' forts in tsplit]
                        
                        # parse each block and merge back
                        ptok_blocks, ptree_blocks = list(), list()
                        for tblock in textblocks:
                            doc = nlp(tblock)
                            ptok_blocks += tokenize(doc)
                            ptree_blocks += parsetrees(doc)
                            del doc
                        
                        # combine block results into paragraphs
                        par_toks.append(ptok_blocks)
                        par_ptrees.append(ptree_blocks)
                        
                    full_text = '\n\n'.join(text_pars)

                    db.insert_doc(idx, par_toks, par_ptrees, full_text, title, author, formaturi, 
                        language, rights, subject, ifnotunique='replace')
                
if __name__ == '__main__':
    parser = GutenParser('db/gutenberg16.db')
    parser.parse_gutenberg(workers=None, verbose=True)
    