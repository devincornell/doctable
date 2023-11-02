
import datetime

import sys
sys.path.append('..')
import doctable

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