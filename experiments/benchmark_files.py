
#from .doctable import DocTable, DocTableRow
#from .util import Timer
import sys
sys.path.append('..')
import doctable
import pickle
import os
import typing
from dataclasses import dataclass, field
import random
import time

@doctable.schema(require_slots=False)
class TestObjBase:
    idx: int = doctable.IDCol()
    size: int = 10000000
    def __post_init__(self):
        if self.data is None:
            self.data = [random.randrange(10**12)]*self.size

@dataclass
class TestObj1(TestObjBase):
    data: list = doctable.Col(None)

@dataclass
class TestObj2(TestObjBase):
    data: list = doctable.Col(None, coltype='picklefile', type_args=dict(folder='tmp'))

def run_benchmark(num_vals = 10):

    tmp = doctable.TempFolder('tmp')
    
    timer = doctable.Timer('creating databases', logfile=tmp.joinpath('log.txt'))
    db1 = doctable.DocTable(schema=TestObj1, target=tmp.joinpath('1.db'), new_db=True)
    db2 = doctable.DocTable(schema=TestObj2, target=tmp.joinpath('2.db'), new_db=True)
    db2.clean_col_files('data')

    timer.step('creating synthetic data')
    data1 = [TestObj1(i) for i in range(num_vals)]
    data2 = [TestObj2(i) for i in range(num_vals)]

    timer.step('insert into table directly')
    db1.insert(data1)

    timer.step('insert into a column file')
    db2.insert(data2)

    timer.step('finished inserting')

    print(f'===========================================')
    print(f'===== Total took: {timer.total_diff()} =================')
    print(f'===========================================')
    #timer.print_table()

if __name__ == '__main__':
    run_benchmark()

