
import sys
os.path.append('....')
import doctable

class GutenDocs(doctable.DocTable):
    tabname = 'gutendocs'
    schema = (
        ('integer', 'id', dict(primary_key=True, autoincrement=True)),
        ('integer', 'year', dict(unique=True, nullable=False)),
        ('string','president'),
        ('string','party'), ('check_constraint', 'party in ("R","D")'),
        ('integer','num_pars'),
        ('integer','num_sents'),
        ('integer', 'num_toks'),
        ('pickle','par_sents'), # nested tokens within sentences within paragraphs
        ('index', 'ind_yr', ['year'], dict(unique=True)),        
    )
    def __init__(self, **kwargs):
        doctable.DocTable.__init__(self, schema=self.schema, tabname=self.tabname, **kwargs)
        
    def insert_nssdoc(self, year, par_sents, prez, party, **kwargs):
        self.insert({
            'fname': year,
            'president': prez,
            'party': party,
            'num_pars': len(par_sents),
            'num_sents': len([s for par in par_sents for s in par]),
            'num_toks': len([t for par in par_sents for s in par for t in s]),
            'par_sents': par_sents,
        }, **kwargs)
    




    