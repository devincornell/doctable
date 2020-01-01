
import sys
sys.path.append('..')
import doctable

def chunk_thread(elchunk):
    for i in elchunk:
        print(i)

if __name__ == '__main__':
    elements = list(range(100))
    with doctable.Distribute() as d:
        d.chunkmap(elements, chunk_thread)
    print('finished.')
    
    