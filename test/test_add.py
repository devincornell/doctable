#from pprint import pprint
#from timeit import default_timer as timer
import os


from testdata import get_sklearn_newsgroups

import sys
sys.path.append('..')
from doctable import DocTable


class SimpleNewsGroups(DocTable):
    def __init__(self, fname):
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

def setup(fname='1321564113.db', ndocs=100):
    sng = SimpleNewsGroups(fname)
    ddf = get_sklearn_newsgroups(ndocs)
    return sng, ddf, fname
    
def tearme(fname):
    os.remove(fname)
    
    
def test_add_sequential():
    fname = 'add_sequential.db'
    sng, ddf, fname = setup(fname, 100)
    
    for ind,dat in ddf.iterrows():
        row = {'file_id':int(dat['filename']), 'category':dat['target'], 'raw_text':dat['text']}
        sng.add(row, ifnotunique='replace')
    
    compare_data_tables(ddf,sng)
    
    tearme(fname)
        
def test_add_many():
    fname = 'add_many.db'
    sng, ddf, fname = setup(fname, 100)
    
    col_order = ('file_id','category','raw_text')
    data = [(dat['filename'],dat['target'],dat['text']) for ind,dat in ddf.iterrows()]
    sng.addmany(data,keys=col_order, ifnotunique='replace')
    
    compare_data_tables(ddf,sng)
    tearme(fname)
    
    
def compare_data_tables(df,sng):
    '''
        Compares data in sng to df.
    '''
    sdf = sng.getdf()
    
    for ind,d in df.iterrows():
        assert(int(d['filename']) in list(sdf['file_id']))
        
        msdf = sdf[sdf['file_id'] == int(d['filename'])]
        assert(msdf.shape[0] == 1)
        
        assert(msdf.iloc[0]['category'] == d['target'])
        assert(msdf.iloc[0]['raw_text'] == d['text'])

    
if __name__ == '__main__':
    test_add_sequential()
    test_add_many()
    
    
    
'''
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
'''
