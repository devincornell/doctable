
#import sqlalchemy as sa





class Timer:
    """Times a task and outputs the elapsed time to screen and log file. 
          Usage example:
        : with Timer(name = "mytask") as t:
        :     <do my task>
    """
    def __init__(self, name='running code', verbose=True):
        self.name = name
        self.verbose = verbose
        self.message = '{name} took {delta}.'
        if self.verbose:
            print(f'{name}')
    
    def __enter__(self):
        self.start = time.time()
        return self
        
    def __exit__(self, *args):
        self.delta = self.format_date(time.time() - self.start)
        if self.verbose:
            print(self.message.format(name=self.name, delta=self.delta))

    def format_date(self, delta):
        if delta > 60:
            printstr = f'{delta/60:0.2f} minutes'
        elif delta > 3600:
            printstr = f'{delta/3600:0.2f} hours'
        else:
            printstr = f'{delta:0.2f} seconds'
        return printstr

    



def try_print(*args, **kwargs):
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        print(f'[Unicode printing error]')

def read_pickle(fname):
    with open(fname, 'rb') as f:
        d = pickle.load(f)
    return d

def write_pickle(obj, fname):
    with open(fname, 'wb') as f:
        pickle.dump(obj,f)
    
