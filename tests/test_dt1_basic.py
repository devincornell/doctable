




import random


import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt
import pytest

        
def test_init_errors():
    # never actually creates this database
    randdbname = 'randomdbname2349io8oipaudjrtfoajsd.db'
    
    # testing make_new_db
    with pytest.raises(FileNotFoundError):
        dt.DocTable(fname=randdbname, make_new_db=False)
        
    # trying to create new file but didn't provide a column schema
    with pytest.raises(ValueError):
        dt.DocTable(fname=randdbname)
    
    # set to check schema without providing a colschema
    with pytest.raises(ValueError):
        dt.DocTable(check_schema=True)
    

if __name__ == '__main__':
    pass
