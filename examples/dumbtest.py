import multiprocessing
import functools
import time
import sys
sys.path.append('..')
import doctable


#def test1(*args, **kwargs):
#    print(f'worker output: {args=} {kwargs=}')

def test1(x, y, z=1):
    return (x * y) ** z

if __name__ == '__main__':

    #userfunc = functools.partial(test1, 1, z=1)
    #pipe, worker_pipe = multiprocessing.Pipe(duplex=True)
    #target = WorkerProcess(worker_pipe, verbose=self.verbose, logging=self.logging)

    #ctx = multiprocessing.get_context('fork')
    #proc = ctx.Process(
    #    target=test1, 
    #    args=(1, 1),
    #)

    #proc.start()
    #print(proc)
    #time.sleep(2)
    #print(proc)
    worker = doctable.WorkerResource(verbose=True, logging=False)

    with worker.start(test1, y=1, z=1) as w:
        print(w.is_alive())
        time.sleep(3)
        print(f'result: {w.execute(4)}')
        print(w.is_alive())
        status = w.get_status()
    print(status.as_series())
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
