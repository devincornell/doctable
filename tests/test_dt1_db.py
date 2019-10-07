
'''
def __init__(self,
             fname='documents.db', 
             tabname='documents', 
             colschema=('num integer', 'doc blob'),
             constraints=tuple(),
             verbose=False,
             persistent_conn=True,
            ):
'''

import sys
sys.path.append('..')
from doctable import DocTable


class Vanilla(DocTable):
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
        )





class NGWithConstraint(DocTable):
    def __init__(self, fname):
        tabname = 'simplenewsgroups'
        super().__init__(
            fname=fname, 
            tabname=tabname, 
            colschema=(
                'file_id int',
                'category string',
                'raw_text string',
            ),
            constraints=(
                'UNIQUE(file_id,category)',
            )
        )

