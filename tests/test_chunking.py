
import sys
sys.path.append('..')
import doctable

import numpy as np

def test_chunking():
    print(doctable.chunk_slice(12, num_chunks=3))
    print(doctable.chunk_slice(13, chunk_size=3))

    k = 13
    a = np.random.rand(k)
    print(a)
    print([a[s] for s in doctable.chunk_slice(k, chunk_size=3)])
    
    # try a bunch of lengths
    for i in range(105):
        
        # should always have k chunks
        if i >= (k := 5):
            slices = doctable.chunk_slice(i, num_chunks=k)
            assert(len(slices) == k)

        # all but last chunk should be m length
        if i >= (m := 3):
            slices = doctable.chunk_slice(i, chunk_size=m)
            assert(all([(s.stop-s.start) == m for s in slices[:-1]]))



if __name__ == '__main__':
    test_chunking()

