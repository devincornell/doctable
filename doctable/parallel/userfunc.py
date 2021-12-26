
from typing import Callable, Any


class UserFunc:
    '''Contains a user function and data to be passed to it when calling.
    Sent to a process upon init and when function should be changed.
    '''
    __slots__ = ['func', 'args', 'kwargs']
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __repr__(self):
        argstr = ', '.join(self.args)
        kwargstr = ', '.join([f'{k}={v}' for k,v in self.kwargs.items()])
        return f'{self.__class__.__name__}({self.func.__name__}(x, {argstr}, {kwargstr}))'

    def execute(self, data: Any):
        '''Call function passing *args and **kwargs.
        '''
        if self.func is None:
            raise WorkerHasNoUserFunctionError()
        return self.func(data, *self.args, **self.kwargs)

