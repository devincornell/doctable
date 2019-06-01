from doctable import DocTable

class NewsGroups(DocTable):
    def __init__(self, fname, persistent_conn=True):
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
            persistent_conn=persistent_conn,
        )
        
        # create indices on file_id and category
        self.query("create index if not exists idx1 on "+tabname+"(file_id)")
        self.query("create index if not exists idx2 on "+tabname+"(category)")
        
        
if __name__ == '__main__':
    

    
    ng = NewsGroups('testme2.db', persistent_conn=False)
    ng.add(dict(file_id=12, category='dude'))
    ng.add(dict(file_id=11, category='hie'))
    
    ng = NewsGroups('testme3.db')
    ng.add(dict(file_id=12, category='dude'))
    ng.add(dict(file_id=11, category='hie'))
    
    ng = NewsGroups('testme.db')
    ng.add(dict(file_id=12, category='dude'))
    ng.add(dict(file_id=11, category='hie'))
    