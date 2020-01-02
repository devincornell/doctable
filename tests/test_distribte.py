
import sys
sys.path.append('..')
import doctable

def chunk_thread(elchunk):
    #print('this thread has {} elements ({} are first)'.format(len(elchunk), elchunk[:3]))
    return [i*2 for i in elchunk]

def thread_func(i):
    return i * 2

def test_basic():
    elements = list(range(100))
    res = [i*2 for i in elements]
    
    for NCORES in (1,3):
        with doctable.Distribute(NCORES) as d:
            el1 = d.map_chunk(chunk_thread, elements)
            el2 = d.map_insert(thread_func, elements)

        assert(len(elements) == len(el1))
        assert(len(elements) == len(el2))
        assert(all([r==e for r,e in zip(res,el1)]))
        assert(all([r==e for r,e in zip(res,el2)]))

if __name__ == '__main__':
    test_basic()
    
    