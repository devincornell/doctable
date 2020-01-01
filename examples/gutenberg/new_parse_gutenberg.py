
from glob import glob
import os
import zipfile
import re
from tqdm import tqdm
import spacy
from gutendocsdb import GutenDocsDB

#from gutenberg.acquire import set_metadata_cache
#from gutenberg.acquire.metadata import SqliteMetadataCache
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
        
        # for whatever reason I think this is currently the last book
        self.ids = list(range(61041))
        
        
    def parse_gutenberg(self, workers=None, verbose=False):
        '''Parse and store nss docs into a doctable.
        Args:
            years (list): years to request from the nss corpus
            dbfname (str): fname for DocTable to initialize in each process.
            workers (int or None): number of processes to create for parsing.
        '''
        db = GutenDocsDB(fname=self.dbfname) # create database file and table and folders
        db.clean_col_files('text')
        db.clean_col_files('par_toks')
        db.clean_col_files('par_ptrees')

        self.distribute_chunks(self.parse_guten_chunk, self.ids, self.nlp, self.dbfname, 
                               verbose, workers=workers)
    
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
            print('getting lang for', i, idx)
            language = get_metadata('language', idx)
            print('lang', language)
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

                    par_toks = list()
                    par_ptrees = list()
                    for doc in nlp.pipe(text_pars):
                        par_toks.append( tokenize(doc) )
                        par_ptrees.append( parsetrees(doc) )
                    full_text = '\n\n'.join(text_pars)

                    db.insert_doc(idx, par_toks, par_ptrees, full_text, title, author, formaturi, 
                        language, rights, subject, ifnotunique='replace')
                
if __name__ == '__main__':
    parser = GutenParser('gutenberg7.db')
    parser.parse_gutenberg(workers=3, verbose=True)
    