
import sys
sys.path.append('..')
import doctable

import numpy as np

def test_chunking():

    # random printing for convenience
    print(doctable.chunk_slice(12, num_chunks=3))
    print(doctable.chunk_slice(13, chunk_size=3))

    # demonstrating use case
    k = 7
    a = np.random.rand(k)
    print(a)
    print([a[s] for s in doctable.chunk_slice(k, chunk_size=3)])
    
    # try a bunch of lengths
    for i in range(105):
        
        # should always have k chunks
        for k in range(2, 30):
            if i >= k:
                slices = doctable.chunk_slice(i, num_chunks=k)
                assert(len(slices) == k)

        # all but last chunk should be m length
        for m in range(2, 30):
            if i >= m:
                slices = doctable.chunk_slice(i, chunk_size=m)
                assert(all([(s.stop-s.start) == m for s in slices[:-1]]))

    # make sure .chunk() works by re-building a list and comparing with original
    items = list(range(90874))
    for l in range(2, 10):
        items_duplicate = list()
        for item_chunk in doctable.chunk(items, num_chunks=l):
            items_duplicate += item_chunk
        assert(items == items_duplicate)

        items_duplicate = list()
        for item_chunk in doctable.chunk(items, chunk_size=l):
            items_duplicate += item_chunk
        assert(items == items_duplicate)
        



if __name__ == '__main__':
    test_chunking()

