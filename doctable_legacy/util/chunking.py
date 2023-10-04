from typing import Iterable, List

def chunk(elements: Iterable, /, chunk_size: int = None, num_chunks: int = None) -> List[Iterable]:
    '''Break elements into chunks determined by chunk_kwargs sent to .chunk_slice().
    '''
    slices = chunk_slice(len(elements), chunk_size=chunk_size, num_chunks=num_chunks)
    return [elements[s] for s in slices]


def chunk_slice(n: int, /, chunk_size: int = None, num_chunks: int = None) -> List[slice]:
    '''Create slices for chunks of an array of size n.
    '''
    if (chunk_size is None and num_chunks is None) or \
        (chunk_size is not None and num_chunks is not None):
        raise ValueError('Exactly one of chunk_size or num_chunks should be specified.')

    # determine number of chunks
    if chunk_size is not None:
        num_chunks = n // chunk_size + (1 if (n % chunk_size) > 0 else 0)
    
    # determine chunk size
    elif num_chunks is not None:
        chunk_size = n // num_chunks + (1 if (n % num_chunks) > 0 else 0)
    
    return [slice(*slice(i*chunk_size, (i+1)*chunk_size).indices(n)) for i in range(num_chunks)]

        
    
    

    



