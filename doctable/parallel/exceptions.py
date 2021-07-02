import doctable

class WorkerIsDeadError(Exception):
    def __init__(self, functionality: str, pid: int, *args, **kwargs):
        message = f'Worker {pid} cannot {functionality} because it is closed.'
        super().__init__(message, *args, **kwargs)

class UnidentifiedMessageReceived(Exception):
    def __init__(self, pid: int, *args, **kwargs):
        message = f'Worker {pid} received an invalid message.'
        super().__init__(message, *args, **kwargs)

class WorkerHasNoUserFunction(Exception):
    def __init__(self, pid: int, *args, **kwargs):
        message = (f'Worker {pid} was not provided with a function. '
            'Either provide a function when the worker is created '
            'or update the worker\'s function using '
            '.update_userfunc().')
        super().__init__(message, *args, **kwargs)

no_function_error_msg = ('Worker {pid} was not provided '
    'with a function. Either provide a function when '
    'the worker is created or send a NewFunction via '
    'the pipe.')

