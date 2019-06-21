
import email

from example_helper import get_sklearn_newsgroups # for this example

from doctable import DocTable # this will be the table object we use to interact with our database.

ddf = get_sklearn_newsgroups(100)
#ddf.head(3)


# this class will represent the doctable. It inherits from DocTable a number of add/query/remove functions.
# of course, you can add any additional methods to this class definition as you find useful.
class NewsGroups(DocTable):
    def __init__(self, fname):
        '''
            DocTable class.
            Inputs:
                fname: fname is the name of the new sqlite database that will be used for instances of class.
        '''
        tabname = 'newsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema='id integer primary key autoincrement, file_id int, category string, \
                raw_text string, subject string, author string, tokenized_text blob, UNIQUE(file_id)',
        )
        
        # create indices on file_id and category
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")


        
sng = NewsGroups('news_group.db')
print('shit')
print(sng)


# add in raw data
col_order = ('file_id','category','raw_text')
data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
sng.addmany(data,keys=col_order, ifnotunique='ignore')


query = sng.get(sel=('file_id','raw_text',), asdict=False)
for fid,text in query:
    
    dat = {'tokenized_text':text.split(),}
    sng.update(dat, 'file_id == {}'.format(fid))


    
query = sng.get(sel=('file_id','raw_text',), asdict=False)
for fid,text in query:
    e = email.message_from_string(text)
    auth = e['From'] if 'From' in e.keys() else ''
    subj = e['Subject'] if 'Subject' in e.keys() else ''
    tok = e.get_payload().split()
    dat = {
        'tokenized_text':tok,
        'author':auth,
        'subject':subj,
    }
    
    sng.update(dat, 'file_id == {}'.format(fid))
    

print(sng.getdf(limit=3))



































