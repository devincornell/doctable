
from glob import glob
import os
import zipfile
import re
from tqdm import tqdm
import spacy
from gutendocsdb import GutenDocsDB

import sys
sys.path.append('...')
import doctable

class GutenParser(doctable.DocParser):
    ''''''
    
    def __init__(self, dbfname, metadata=None, data_folder='data/aleph.gutenberg.org/', 
                 *args, **kwargs):
        self.nlp = spacy.load('en')
        self.dbfname = dbfname
        self.metadata = metadata
        
        self.fnames = glob(data_folder+'/**/*.zip', recursive=True)
        
        
    def parse_gutenberg(self, as_parsetree=False, workers=None, verbose=False):
        '''Parse and store nss docs into a doctable.
        Args:
            years (list): years to request from the nss corpus
            dbfname (str): fname for DocTable to initialize in each process.
            as_parsetree (bool): store parsetrees (True) or tokens (False)
            workers (int or None): number of processes to create for parsing.
        '''
        db = GutenDocsDB(fname=dbfname) # create database file and table and folders
        
        self.distribute_chunks(self.parse_guten_chunk, self.fnames, self.nlp, self.dbfname, 
                               as_parsetree, verbose, self.metadata, workers=workers)
    
    @classmethod
    def parse_guten_chunk(cls, fnames, nlp, dbfname, as_parsetree, verbose, metadata):
        '''Runs in separate process for each chunk of nss docs.
        Description: parse each fname and store into database
        Args:
            fnames (list<str>): list of filenames to read
            nlp (spacy parser): parser
            dbfname (str): filename of database to write into
            verbose (bool): print progress
            metadata (dict<>): metadata to insert into database
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
        
        if not as_parsetree:
            parse_func = tokenize
        else:
            parse_func = parsetrees
        
        n = len(fnames)
        empty_ct, read_ct = 0, 0
        for i, fname in tqdm(enumerate(fnames), total=n, ncols=50):
            text_pars = cls.read_file(fname, re_start)
            if text_pars is None:
                empty_ct += 1
            else:
                read_ct += 1
                parsed_pars = list()
                for text_par,doc in zip(text_pars,nlp.pipe(text_pars)):
                    parsed = parse_func(doc)
                    parsed_pars.append(parsed)
                text = '\n\n'.join(text_pars)
                db.insert_doc(fname, parsed_pars, text, ifnotunique='replace')
        print(f'thread finished parsing {read_ct} with {empty_ct} empty.')

    @staticmethod
    def read_file(fname, re_start):
        base = os.path.basename(fname)
        textname = os.path.splitext(base)[0] + '.txt'

        with zipfile.ZipFile(fname) as z:
            try:
                text = z.read(textname).decode(encoding='utf-8', errors='ignore')
                text_was_found = True
            except KeyError:
                text_was_found = False
        if text_was_found:
            match = re.search(re_start, text)
            if match is not None:
                text_pars = [par.strip() for par in text[match.end():].split('\n\n') 
                             if len(par.strip()) > 0]
                return text_pars
            else:
                return None
        
if __name__ == '__main__':
    parser = GutenParser('gutenberg_trees.db')
    parser.parse_gutenberg(as_parsetree=True, verbose=True)
    