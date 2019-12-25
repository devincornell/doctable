
import sys
sys.path.append('....')
import doctable

class GutenDocsDB(doctable.DocTable):
    tabname = 'gutendocs'
    schema = (
        ('integer', 'id', dict(primary_key=True, autoincrement=True)),
        ('string', 'fname', dict(nullable=False)),
        ('pickle','par_sents'), # nested tokens within sentences within paragraphs
        ('index', 'ind_fname', ['fname'], dict(unique=True)),        
    )
    def __init__(self, **kwargs):
        doctable.DocTable.__init__(self, schema=self.schema, tabname=self.tabname, **kwargs)
        
    def insert_doc(self, fname, par_sents, **kwargs):
        self.insert({
            'fname': fname,
            'par_sents': par_sents,
        }, **kwargs)
    




    