




import random
import os

import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt
import pytest

schema = (
    ('idcol', 'id'),
    ('integer', 'whateva'),
)    
    
def test_init_errors():
    # never actually creates this database
    randdbname = 'randomdbname2349io8oipaudjrtfoajsd.db'
    
    # new memory db with no schema
    with pytest.raises(ValueError):
        dt.DocTable(target=':memory:')
    print(dt.DocTable(target=':memory:', schema=schema))
        
    # new db with no schema
    with pytest.raises(ValueError):
        dt.DocTable(target=randdbname, new_db=True)
    #print(dt.DocTable(target=randdbname, schema=schema))
        
    # don't want to make db but one doesn't exist
    with pytest.raises(FileNotFoundError):
        dt.ConnectEngine(target=randdbname, new_db=False)


if __name__ == '__main__':
    pass
