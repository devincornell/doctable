
from doctable import DocTable
import glob
import spacy

class NewsArticles(DocTable):
    def __init__(self, fname):
        '''
            This includes examples of init variables. See DocTable class for complete list of options.
        '''
        super().__init__(
            fname=fname, 
            tabname='newsarticles', 
            colschema='id integer primary key autoincrement, newssource string, docname string, timestamp int, datestr string, fname string, text string, bow blob',
        )
        
        # NOTICES: references tabname defined in the above __init__ function
        # extra commands to create index tables for fast lookup
        self.query("create index if not exists idx1 on newsarticles(timestamp)")
        self.query("create index if not exists idx2 on newsarticles(newssource)")
        self.query("create index if not exists idx3 on newsarticles(newssource,timestamp)")


