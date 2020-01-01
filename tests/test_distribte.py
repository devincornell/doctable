
import sys
sys.path.append('..')
import doctable

def chunk_thread(elchunk):
    for i in elchunk:
        print(i)
def thread_func(i):
    print(i)
    if i == 5:
        raise KeyError()

if __name__ == '__main__':
    elements = list(range(10))
    with doctable.Distribute(2) as d:
        d.map_chunk(chunk_thread, elements)
        print('--------')
        d.map_insert(thread_func, elements)
        
    print('finished.')
    
    