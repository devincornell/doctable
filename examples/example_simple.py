from pprint import pprint
from timeit import default_timer as timer

from example_helper import get_sklearn_newsgroups

from doctable import DocTable # this will be the table object we use to interact with our database.

ddf = get_sklearn_newsgroups()
print(ddf.head(3))


# this class will represent the doctable. It inherits from DocTable a number of add/query/remove functions.
# of course, you can add any additional methods to this class definition as you find useful.
class SimpleNewsGroups(DocTable):
    def __init__(self, fname):
        '''
            This includes examples of init variables. See DocTable class for complete list of options.
            Inputs:
                fname: fname is the name of the new sqlite database that will be used for this class.
        '''
        tabname = 'simplenewsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema=(
                'id integer primary key autoincrement',
                'file_id int',
                'category string',
                'raw_text string',
            ),
            constraints=(
                'UNIQUE(file_id)',
            )
        )
        
        # this section defines any other commands that should be executed upon init
        # NOTICE: references tabname defined in the above __init__ function
        # extra commands to create index tables for fast lookup
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")




sng = SimpleNewsGroups('simple_news_group3.db')
print(sng)

# adds data one row at a time. Takes longer than bulk version
start = timer()

for ind,dat in ddf.iterrows():
    row = {'file_id':int(dat['filename']), 'category':dat['target'], 'raw_text':dat['text']}
    sng.add(row, ifnotunique='replace')

print((timer() - start)*1000, 'mil sec.')
print(sng)


# adds tuple data in bulk by specifying columns we are adding
start = timer()

col_order = ('file_id','category','raw_text')
data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
sng.addmany(data,keys=col_order, ifnotunique='replace')

print((timer() - start)*1000, 'mil sec.')
print(sng)

result = sng.get(
    sel=('file_id','raw_text'), 
    where='category == "rec.motorcycles"', 
    orderby='file_id ASC', 
    limit=3,
)
for row in result:
    print(str(row['file_id'])+':', row['raw_text'][:50])


result_df = sng.getdf(
    sel=('file_id','raw_text'), 
    where='category == "rec.motorcycles"', 
    orderby='file_id ASC', 
    limit=5,
)
result_df
    
    
    
sng.update({'category':'nevermind',},where='file_id == "103121"')
sng.getdf(where='file_id == "103121"') # to see update, look at "category" column entry
    