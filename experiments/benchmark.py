
from .doctable import DocTable, DocTableRow
from .util import Timer
import pickle
import os
from dataclasses import dataclass, field

@dataclass
class TestObj(DocTableRow):
    i: int
    name: str = None
    value: float = None
    def __post_init__(self):
        self.name = str(self.i)
        self.value = (self.i / 0.001)**2


def run_benchmark(fname = '.tmp.pic', num_vals = 1000, num_pickle_files = 10):

    timer = Timer('Starting benchmark')

    timer.step('creating synthetic data')
    data = [TestObj(i) for i in range(num_vals)]

    timer.step(f'saving {num_pickle_files} large files with {len(data)} entries')
    for i in range(num_pickle_files):
        with open(fname, 'wb') as f:
            pickle.dump(data, f)

    timer.step(f'saving {len(data)} small files')
    for d in data:
        with open(fname, 'wb') as f:
            pickle.dump(d, f)
    os.remove(fname)

    timer.step(f'inserting separate rows into doctable')
    db = DocTable(schema=TestObj, target=fname, new_db=True)
    for d in data:
        db.insert(d)
    os.remove(fname)

    timer.step(f'inserting many doctable rows at once')
    db = DocTable(schema=TestObj, target=fname, new_db=True)
    db.insert(data)

    timer.step(f'selecting all records')
    selectdata = db.select()

    timer.step(f'selecting some records')
    selectdata = db.select(where=db['i']>len(data)/2)

    os.remove(fname)

    timer.step('finished!')
    if os.path.exists(fname):
        os.remove(fname)

    print(f'===========================================')
    print(f'===== Total took: {timer.total_diff()} =================')
    print(f'===========================================')
    timer.print_table()



