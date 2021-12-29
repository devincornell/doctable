import multiprocessing
import functools
import time
import sys
sys.path.append('..')
import doctable


def test1(x, y, z=1):
    return (x*y)**z

#if __name__ == '__main__':

userfunc = functools.partial(test1, 1, z=1)


with doctable.WorkerResource('fork', verbose=True).start(userfunc) as w:
    print(w.is_alive())
    time.sleep(3)
    print(w.is_alive())
print(w)
print(w.is_alive())
#w.start(userfunc)
#print(w.is_alive())
#time.sleep(1)
#print(w.is_alive())
#print(w)
#print(w.start(str))
#print(w.proc.start())
#print(w.is_alive())
#time.sleep(5)
#print(w.proc.start())
#w.join()
