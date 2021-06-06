import numpy as np
import pandas as pd
from dataclasses import dataclass, field
import cProfile
import tqdm
import datetime
import time
from pprint import pprint

import sys
sys.path.append('..')
import doctable


folder = 'tmp'

@dataclass
class DataObj(doctable.DocTableRow):
    id: int = doctable.IDCol()
    data: np.ndarray = doctable.Col(None)

@dataclass
class FileObj(doctable.DocTableRow):
    id: int = doctable.IDCol()
    data: np.ndarray = doctable.Col(None, coltype='picklefile', type_args=dict(folder=folder))


def print_delta(delta):
    #delta = ts.total_seconds()
    if delta >= 3600:
        s = f'{delta/3600:0.2f} hrs'
    elif delta >= 60:
        s = f'{delta/60:0.2f} min'
    elif delta < 1.0:
        s = f'{delta*1000:0.3f} ms'
    else:
        s = f'{delta:0.2f} sec'
    return s

def av_time(timer):
    prev = timer[0]
    diffs = list()
    for t in timer[1:]:
        diffs.append(t._ts-prev._ts)
        prev = t
    av_diff = sum(diffs, datetime.timedelta(0))/len(diffs)
    #return print_delta(av_diff)
    return av_diff.total_seconds()


def time_call(func, *args, num_calls=10, **kwargs):
    timer = doctable.Timer(verbose=False)
    for i in (range(num_calls)):
        with timer:
            func(*args, **kwargs)
    #print([t._ts for t in timer[1:]])
    return av_time(timer)


class Test:
    def __init__(self, db, wrap_class):
        self.db = db
        self.wrap_class = wrap_class
        self.results = list()

    def __repr__(self):
        return f'{self.wrap_class.__name__}Test'
    
    @property
    def last(self):
        return self.results[-1]

    def run_test(self, sizeGB=0.1, num=10):
        print(f'\t== {self} ==')
        payload = self.make_payload(self.wrap_class, sizeGB=sizeGB, num=num)
        #print(f'\t{self} payload size: {int(1e8 * sizeGB)}')

        # separate lines to guarantee execution order
        delete_time = time_call(lambda: self.db.delete())
        print(f'\t\t{self} delete time: {print_delta(delete_time)}')

        insert_time = time_call(lambda: self.db.insert(payload))
        print(f'\t\t{self} insert time: {print_delta(insert_time)}')

        select_index_time = time_call(lambda: self.db.select("id"))
        print(f'\t\t{self} select index time: {print_delta(select_index_time)}')

        select_payload_time = time_call(lambda: self.db.select())
        print(f'\t\t{self} select payload time: {print_delta(select_payload_time)}')

        self.results.append({
            'type': str(self.wrap_class.__name__),
            'sizeGB': sizeGB,
            'num': num,
            'delete': delete_time,
            'insert': insert_time,
            'select index': select_index_time,
            'select payload': select_payload_time,
        })
        return self.results[-1]

    @staticmethod
    def make_payload(wrap_class, sizeGB, num):
        # 5000000000 (5e9) is 45 GB max, ~38GB stable.
        siz = int(1e8 * sizeGB)
        payload = [wrap_class(data=np.ones(siz)) for i in range(num)]
        return payload

def run_test(ddb, fdb, sizeGB=0.1, num=10):
    
    print(f'========== Running Test (sizeGB={sizeGB}, num={num} ==========')
    #print(f'\t\tTESTING TIMER: {time_call(lambda: time.sleep(2))}')
    #print(f'\t\tTESTING TIMER: {time_call(lambda: time.sleep(3))}')
    #print(f'\t\tTESTING TIMER: {time_call(lambda: time.sleep(4))}')

    print('\t=== Make Payload ===')
    d_payload = make_payload(DataObj, sizeGB=sizeGB, num=num)
    f_payload = make_payload(FileObj, sizeGB=sizeGB, num=num)
    

    print('\t=== Delete ===')
    #cProfile.run('ddb.delete()')
    print(f'\t\tData DB: {time_call(lambda: ddb.delete())}')
    print(f'\t\tFile DB: {time_call(lambda: fdb.delete())}')
    #%time ddb.delete()
    #%time fdb.delete()
    fdb.clean_col_files('data')
    #print()
    
    print('\t=== Insert ===')
    print(f'\t\tData DB: {time_call(lambda: ddb.insert(d_payload))}')
    print(f'\t\tFile DB: {time_call(lambda: fdb.insert(f_payload))}')
    #%timeit ddb.insert(d_payload)
    #%timeit fdb.insert(f_payload)
    #print()
    
    print('\t=== Select Index ===')
    print(f'\t\tData DB: {time_call(lambda: ddb.select("id"))}')
    print(f'\t\tFile DB: {time_call(lambda: fdb.select("id"))}')
    #%timeit a = ddb.select('id')
    #%timeit a = fdb.select('id')
    #print()
    
    print('\t=== Select Payload ===')
    print(f'\t\tData DB: {time_call(lambda: ddb.select())}')
    print(f'\t\tFile DB: {time_call(lambda: fdb.select())}')
    #%timeit a = ddb.select()
    #%timeit a = fdb.select()
    print()


def main():

    # set up database objects
    #folder = '/tmp/devintest'
    
    tmpf = doctable.TempFolder(folder)


    target = f'{folder}/benchmark_fileobj.db'
    ddb = doctable.DocTable(schema=DataObj, target=target, tabname='dataobj', new_db=True)
    ddb.delete()
    test_data = Test(ddb, DataObj)

    fdb = doctable.DocTable(schema=FileObj, target=target, tabname='fileobj', new_db=True)
    fdb.delete() # empty datbases
    fdb.clean_col_files('data')
    test_file = Test(fdb, FileObj)
    print(ddb, fdb)

    params = [
        (0.00001, 100),
        (0.00001, 500),
        (0.00001, 1000),
        (0.00001, 10000),
        (0.00001, 100000),
        
        (0.0001, 100),
        (0.0001, 1000),
        (0.0001, 10000),
        (0.001, 100),
        (0.001, 500),
        (0.001, 1000),

        (0.01, 10),
        (0.01, 50),
        (0.01, 100),

        (0.1, 3),
        (0.1, 5),
        (0.1, 10),
        
        (1.0, 1),
        (1.0, 3),
        (1.0, 5),
    ]

    for sizeGB, num in params:
        print(f'========== Running Test (sizeGB={sizeGB}, num={num}) ==========')

        test_data.run_test(sizeGB=sizeGB, num=num)
        #pprint(test_data.last)
        
        test_file.run_test(sizeGB=sizeGB, num=num)
        #pprint(test_file.last)

        # clearing filesystem
        fdb.clean_col_files('data')

        # save updated version
        df = pd.DataFrame(test_data.results + test_file.results)
        df.to_csv('results/filecol_benchmark_results_hauss.csv', index=False)

        print()


if __name__ == '__main__':
    main()


