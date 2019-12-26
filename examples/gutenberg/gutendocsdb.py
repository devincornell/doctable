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
            ('string', 'fname', dict(nullable=False)),
            ('picklefile', 'par_sents', {}, {'fpath':'_'+dbname+'_parsents'}),
            ('textfile','text', {}, {'fpath':'_'+dbname+'_texts'}),
            ('index', 'ind_fname', ['fname'], dict(unique=True)),
        )
        doctable.DocTable.__init__(self, fname=fname, schema=self.schema, tabname=self.tabname, **kwargs)
        
    def insert_doc(self, fname, par_sents, text, **kwargs):
        self.insert({
            'fname': fname,
            'par_sents': par_sents,
            'text': text,
        }, **kwargs)
    




    