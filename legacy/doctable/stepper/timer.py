
import warnings
from .stepper import Stepper

class Timer(Stepper):
    '''For backwards compatibility purposes ONLY.'''
    def __init__(self, *args, **kwargs):
        warnings.warn('Timer is depricated. Please use Step instead.')
        return super().__init__(*args, **kwargs)
    pass

