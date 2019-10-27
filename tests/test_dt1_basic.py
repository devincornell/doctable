




import random


import sys
sys.path.append('..')
#from doctable import DocTable2, func, op
import doctable as dt
import pytest

def test_make_new_db_flag(n=20):
    with pytest.raises(FileNotFoundError):
        dt.DocTable(fname='randomdbname2349io889523479.db', make_new_db=False)

if __name__ == '__main__':
    pass
