
import time
import datetime


class Timer:
    """Times a task and outputs the elapsed time to screen and log file. 
          Usage example:
        : with Timer(name = "mytask") as t:
        :     <do my task>
    """
    def __init__(self, message='', verbose=True):
        ''' Add single step for current datetime.
        '''
        self.verbose = verbose

        # add first timestamp
        self.steps = list()
        self.step(message)
    
    def step(self, message=None, verbose=None):
        self.steps.append({'ts':datetime.datetime.now(), 'msg': message})
        
        if (verbose is not None and verbose) or (verbose is None and self.verbose):
            if len(self.steps) == 1:
                print(f'{self.f_ts()}: {self.f_msg()}')
            else:
                print(f'{self.f_ts()}: ({self.f_delta()}) {self.f_msg()}')

    ######################## basic accessors ########################
    def __getitem__(self, ind):
        return self.steps[ind]

    ######################## enter/exit methods ########################
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        self.step(verbose=False)
        if self.verbose:
            print(f'{self.f_ts()}: {self.f_msg(0)} took {self.f_delta()}.')

    ######################## accessing data ########################
    
    def msg(self, ind=None):
        ''' Access message of given index.
        '''
        if ind is None:
            ind = -1
        return self[ind]['msg']

    def ts(self, ind=None):
        ''' Access timestamp of given index.
        '''
        if ind is None:
            ind = -1
        return self[ind]['ts']

    def delta(self, ind=None):
        ''' Difference between last timestep and teh one before it.
        '''
        if ind is None:
            ind = -1
        return self.ts(ind) - self.ts(ind-1)

    ######################## string formatted info ########################
    def f_msg(self, ind=None):
        ''' Return message if it is not None else empty string.
        '''
        msg = self.msg(ind)
        if msg is not None:
            return msg
        else:
            return ''

    def f_ts(self, ind=None):
        ''' Formatted timestamp of given index.
        '''
        return self.ts(ind).strftime('%a %H:%M:%S')
        
    def f_delta(self, ind=None):
        ''' Formatted time delta for the given step.
        '''
        delta = self.delta(ind).total_seconds()
        #print(dir(delta))
        #return f'{delta.hours}:{delta.minutes}:{delta.seconds}'
        if delta >= 3600:
            return f'{delta/3600:0.2f} hrs'
        elif delta >= 60:
            return f'{delta/60:0.2f} min'
        else:
            return f'{delta:0.2f} sec'
    
    def print_table(self):
        print('Timer table:')
        for i, step in enumerate(self.steps):
            print(f'    {self.f_ts(i)}: ({self.f_delta(i)}) {self.f_msg(i)}')


if __name__ == '__main__':
    print('starting')
    def test_func(n=100000000):
        return sum(i for i in range(n))
    
    with Timer('whateva', verbose=False):
        print(test_func())

    timer = Timer('running this shit', verbose=False)
    print(test_func())

    timer.step('whatever this step is')
    print(test_func())

    timer.step('next step')
    print(test_func())

    timer.step('that\'s all folks.')
    timer.print_table()