
import dataclasses
import psutil

def get_mem_bytes(self):
    ''' Get system memory usage in bytes.
    '''
    return psutil.virtual_memory().used

def get_mem_gb(self, *args, **kwargs):
    ''' Get system memory usage in GB.
    '''
    return get_mem_bytes(*args, **kwargs)/1e9


