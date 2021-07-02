

class BaseException(Exception):
    '''Exception template for doctable.'''
    message = None
    def __init__(self, *args, **kwargs):
        super().__init__(self.message, *args, **kwargs)

