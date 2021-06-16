
def format_time(num_seconds: int):
    ''' Get string representing time quantity with correct units.
    '''
    if num_seconds >= 3600:
        return f'{num_seconds/3600:0.2f} hrs'
    elif num_seconds >= 60:
        return f'{num_seconds/60:0.2f} min'
    elif num_seconds < 1.0:
        return f'{num_seconds*1000:0.2f} ms'
    else:
        return f'{num_seconds:0.2f} sec'

def format_memory(num_bytes: int):
    ''' Get string representing memory quantity with correct units.
    '''
    if num_bytes >= 1e9:
        return f'{num_bytes/1e9:0.2f} GB'
    elif num_bytes >= 1e6:
        return f'{num_bytes/1e6:0.2f} MB'
    elif num_bytes >= 1e3:
        return f'{num_bytes*1e3:0.3f} kB'
    else:
        return f'{num_bytes:0.2f} Bytes'



