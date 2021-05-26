import numpy as np
from dataclasses import dataclass, field
import cProfile
import tqdm
import datetime
import time

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


def make_payload(wrap_class, sizeGB=0.1, num=10):
    # 5000000000 (5e9) is 45 GB max, ~38GB stable.
    siz = int(1e8 * sizeGB)
    print(f'\tpayload size: {siz}')
    payload = [wrap_class(data=np.ones(siz)) for i in range(num)]
    return payload

def print_delta(ts):
    delta = ts.total_seconds()
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
    return print_delta(av_diff)


def time_call(func, *args, num_calls=10, **kwargs):
    timer = doctable.Timer(verbose=False)
    for i in (range(num_calls)):
        with timer:
            func(*args, **kwargs)
    #print([t._ts for t in timer[1:]])
    return av_time(timer)


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

    fdb = doctable.DocTable(schema=FileObj, target=target, tabname='fileobj', new_db=True)
    fdb.delete() # empty datbases
    fdb.clean_col_files('data')
    print(ddb, fdb)

    run_test(ddb, fdb, sizeGB=0.0001, num=10000)
    run_test(ddb, fdb, sizeGB=0.001, num=1000)
    run_test(ddb, fdb, sizeGB=0.01, num=100)
    run_test(ddb, fdb, sizeGB=0.1, num=10)
    run_test(ddb, fdb, sizeGB=1.0, num=5)


if __name__ == '__main__':
    main()


