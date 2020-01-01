import os
import sys
sys.path.append('../..')
import doctable
#import ..doctable

class GutenDocsDB(doctable.DocTable):
    tabname = 'gutendocs'
    def __init__(self, fname, **kwargs):
        bn = os.path.basename(fname)
        dbname = os.path.splitext(bn)[0]
        self.schema = (
            ('idcol', 'id'),
            #('string', 'fname', dict(nullable=False)),
            ('integer', 'gutenid'),
            ('string', 'title', {'unique':True}),
            ('string', 'author'),
            ('string', 'formaturi'),
            ('string', 'language'),
            ('string', 'rights'),
            ('string', 'subject'),
            
            # book text data
            ('picklefile', 'par_ptrees', {}, {'fpath': dbname+'_ptrees'}),
            ('picklefile', 'par_toks', {}, {'fpath': dbname+'_toks'}),
            ('textfile','text', {}, {'fpath': dbname+'_texts'}),
            
            # convenient metadata
            ('integer', 'num_pars'),
            ('integer', 'num_sents'),
            ('integer', 'num_toks'),
            #('index', 'ind_fname', ['fname'], dict(unique=True)),
        )
        doctable.DocTable.__init__(self, fname=fname, schema=self.schema, 
            tabname=self.tabname, **kwargs)
        
    def insert_doc(self, gutenid, par_toks, par_ptrees, full_text, title, 
        author, formaturi, language, rights, subject, **kwargs):
        self.insert({
            'gutenid': gutenid,
            'title': title,
            'author': author,
            'formaturi': formaturi,
            'language': language,
            'rights': rights,
            'subject': subject,
            
            'par_toks': par_toks,
            'par_toks': par_ptrees,
            'full_text': text,
            'num_pars': len(par_sents),
            'num_sents': len([s for par in par_sents for s in par]),
            'num_toks': len([t for par in par_sents for s in par for t in s]),
        }, **kwargs)
    




    